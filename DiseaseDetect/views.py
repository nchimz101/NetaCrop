from PIL import Image
from tensorflow.keras.preprocessing import image
import warnings
import sys
import numpy as np
from PIL import Image, ImageOps
from .models import PlantDetect
from django.shortcuts import render, HttpResponseRedirect
from .form import PlantInfo
# After api hit
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from .serializers import Imageserializer, DiseaseDetectSerializer
from rest_framework.parsers import FileUploadParser
from django.conf import settings
# GETAPI


class DiseaseList(APIView):

    def get(self, request):

        detected1 = PlantDetect.objects.all()
        serialzer = DiseaseDetectSerializer(detected1, many=True)
        return Response(serialzer.data)


class uploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request):
        file = request.data.get('file', None)
        # print(file)
        if file:
            return Response({"message": 'File is recieved'}, status=200)


# MAIN APP INTERFACE

def app(request):
    import os
    if request.method == 'POST':
        form = PlantInfo(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['userimage']
            # print(request.FILES)

            import string
            import random

            def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
                a = ''.join(random.choice(chars) for _ in range(size))
                return a

            img = id_generator()
            # print(img)
            with open(os.path.join(settings.BASE_DIR, f"media/images/test_img{img}.jpg"), 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            # print("Uploaded")

            # Trained_Model_path
            h5_path = os.path.join(
                settings.BASE_DIR, 'DiseaseDetect/keras_model.h5')

            main_path = os.path.join(
                settings.BASE_DIR, f"media/images/test_img{img}.jpg")

            a = f"/images/test_img{img}.jpg"
            # print("The main file path",a)

            from tensorflow.keras.models import load_model
            model = load_model(h5_path)  # model

            predicted_value = model_predict(
                main_path, model)  # Imagepath and model

            description = disease_descriptor(predicted_value)

            remedy = remedy_detail(predicted_value)

            plantname = plant_name(predicted_value)

            scificname = scific_name(predicted_value)

            tomatodesc = tomato_desc(predicted_value)

            if tomatodesc == 'None':
                return render(request, "error.html")

            else:
                Submit_Disease = PlantDetect(
                    userimage=a, disease_name=predicted_value)
                Submit_Disease.save()

                img_view = PlantDetect.objects.latest('id')

                return render(request, "result.html", {'ans': predicted_value, 'desc': description, 'remedy': remedy, 'img': img_view, 'name': plantname, 'scific': scificname, 'tomatodesc': tomatodesc})

    else:
        form = PlantInfo()
    return render(request, 'index.html', {'form': form})


def mycollection(request):
    if request.method == 'GET':
        # getting all the objects of hotel.
        review = PlantDetect.objects.all()
        return render(request, 'collection.html', {'info': review})


def aboutus(request):
    if request.method == 'GET':
        # getting all the objects of hotel.
        # review = PlantDetect.objects.all()
        return render(request, 'about.html')

# MODEL PREDICTOR


warnings.filterwarnings('ignore')


def model_predict(img_path, model):
    # print(img_path)
    import cv2
    import numpy as np
    img = cv2.imread(img_path)
    grid_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    grid_HSV = cv2.cvtColor(grid_RGB, cv2.COLOR_RGB2HSV)  # Converting to HSV
    lower_green = np.array([25, 52, 72])
    upper_green = np.array([102, 255, 255])

    lower_yellow = np.array([22, 93, 0])
    upper_yellow = np.array([45, 255, 255])

    mask = cv2.inRange(grid_HSV, lower_green, upper_green)

    mask_yellow = cv2.inRange(grid_HSV, lower_yellow, upper_yellow)

    # print("Green Part of Image")
    green_perc = (mask > 0).mean()
    # print(green_perc)

    # print("Yellow percent")
    yellow_perc = (mask_yellow > 0).mean()
    # print(yellow_perc)

    if green_perc > 0.2:
        # print("More")
        img = image.load_img(img_path, target_size=(224, 224))

        # Preprocessing the image
        x = image.img_to_array(img)
        x = np.true_divide(x, 255)

        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        preds = np.argmax(preds, axis=1)
        if preds == 0:
            preds = "Cassava_Bacterial_Blight"
        elif preds == 1:
            preds = "Cassava_Brown_Streak_Virus_Disease"
        elif preds == 2:
            preds = "Cassava_Green_Mite"
        elif preds == 3:
            preds = "Cassava_healthy"
        elif preds == 4:
            preds = "Cassava_Mosaic_Disease"
        elif preds == 5:
            preds = "Corn_(maize)___Common_rust"
        elif preds == 6:
            preds = "Corn_(maize)___healthy"
        elif preds == 7:
            preds = "Corn_(maize)___Northern_Leaf_Blight"
        elif preds == 8:
            preds = "Corn_(maize)_Gray_Leaf_Spot"
        elif preds == 9:
            preds = "Tomato-Leaf___Bacterial_spot"
        elif preds == 10:
            preds = "Tomato-Leaf_Early_blight"
        elif preds == 11:
            preds = "Tomato-Leaf_healthy"
        elif preds == 12:
            preds = "Tomato-Leaf_Late_blight"
        elif preds == 13:
            preds = "Tomato-Leaf_Tomato_Yellow_Leaf_Curl_Virus"

        # print (preds)
        return preds
    else:
        return "Not Recognized"


# Disease Description
def disease_descriptor(disease_name):
    if disease_name == "Cassava_Bacterial_Blight":
        desc = '''  Manihotis is the pathogen that causes bacterial blight of cassava. 
        Manihotis is a vascular and foliar pathogenic species of bacteria. It normally enters its host plants through stomatal openings or hydathodes. Wounds to stems have also been noted as a means of entry. Once inside its host. 
        Axonopodis enzymatically dissolves barriers to the plant's vascular system and so begins a systemic infection. Because of its enzymes inability to break down highly lignified cell walls, this pathogen prefers to feed on younger tissues and often follows xylem vessels into developing buds and seeds. Seeds which have been invaded by a high number of bacteria are sometimes deformed and necrotic, but assays have shown a high percentage of infected seeds are asymptomatic carriers.'''

    elif disease_name == "Cassava_Brown_Streak_Virus_Disease":
        desc = '''Cassava brown streak virus disease (CBSD) is a damaging disease of cassava plants, and is especially troublesome in East Africa. It was first identified in 1936 in Tanzania, and has spread to other coastal areas of East Africa, from Kenya to Mozambique. Recently, it was found that two distinct viruses are responsible for the disease: cassava brown streak virus (CBSV) and Ugandan cassava brown streak virus (UCBSV).
        Root rot renders the cassava tuber inedible, resulting in severe loss of economic value; therefore, current research focuses on achieving cultivars that do not develop the necrotic rot.
        This disease is considered to be the biggest threat to food security in coastal East Africa and around the eastern lakes.'''

    elif disease_name == "Cassava_Green_Mite":
        desc = '''The cassava green mite, Mononychellus tanajoa, is an indigenous pest of cassava, Manihot esculenta, in the Neotropics. The mite became a major pest of cassava across equatorial Africa following introduction in the early 1970s'''

    elif disease_name == "Cassava_healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Cassava_Mosaic_Disease":
        desc = '''Cassava mosaic virus is the common name used to refer to any of eleven different species of plant pathogenic virus in the genus Begomovirus. African cassava mosaic virus (ACMV), East African cassava mosaic virus (EACMV), and South African cassava mosaic virus (SACMV) are distinct species of circular single-stranded DNA viruses which are transmitted by whiteflies and primarily infect cassava plants; these have thus far only been reported from Africa. Related species of viruses (Indian cassava mosaic virus, ICMV) are found in India and neighbouring islands (Sri Lankan cassava mosaic virus, SLCMV), though cassava is cultivated in Latin America as well as Southeast Asia. Nine species of cassava-infecting geminiviruses have been identified between Africa and India based on genomic sequencing and phylogenetic analysis. This number is likely to grow due to a high rate of natural transformation associated with CMV.'''

    elif disease_name == "Corn_(maize)___Northern_Leaf_Blight":
        desc = '''Southern corn leaf blight (SCLB) is a fungal disease of maize caused by the plant pathogen Bipolaris maydis (also known as Cochliobolus heterostrophus in its teleomorph state).

The fungus is an Ascomycete and can use conidia or ascospores to infect.[1] There are three races of B. maydis: Race O, Race C, and Race T; SCLB symptoms vary depending on the infectious pathogen's race. Race T is infectious to corn plants with the Texas male sterile cytoplasm (cms-T cytoplasm maize) and this vulnerability was the cause of the United States SCLB epidemic of 1969-1970[2] For this reason, Race T is of particular interest. While SCLB thrives in warm, damp climates, the disease can be found in many of the world's maize-growing areas.[3] Typical management practices include breeding for host resistance, cultural controls and fungicide use.'''

    elif disease_name == "Corn_(maize)___Common_rust":
        desc = '''Common corn rust, caused by the fungus Puccinia sorghi, is the most frequently occurring of the two primary rust diseases of corn in the U.S., but it rarely causes significant yield losses in Ohio field (dent) corn. Occasionally field corn, particularly in the southern half of the state, does become severely affected when weather conditions favor the development and spread of the rust fungus. Sweet corn is generally more susceptible than field corn. In years with exceptionally cool summers, and especially on late-planted fields or sweet corn, yield losses may occur when the leaves at and above the ears become severely diseased before grain fill is complete.

'''

    elif disease_name == "Corn_(maize)_Gray_Leaf_Spot":
        desc = '''Grey leaf spot (GLS) is a foliar fungal disease that affects maize, also known as corn. GLS is considered one of the most significant yield-limiting diseases of corn worldwide.[1] There are two fungal pathogens that cause GLS: Cercospora zeae-maydis and Cercospora zeina.[2][3][4] Symptoms seen on corn include leaf lesions, discoloration (chlorosis), and foliar blight. Distinct symptoms of GLS are rectangular, brown to gray necrotic lesions that run parallel to the leaf, spanning the spaces between the secondary leaf veins.[1] The fungus survives in the debris of topsoil and infects healthy crops via asexual spores called conidia. Environmental conditions that best suit infection and growth include moist, humid, and warm climates.[5][3][4] Poor airflow, low sunlight, overcrowding, improper soil nutrient and irrigation management, and poor soil drainage can all contribute to the propagation of the disease'''

    elif disease_name == "Corn_(maize)___healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Tomato-Leaf___Bacterial_spot":
        desc = '''Bacterial spot is caused by four species of Xanthomonas and occurs worldwide wherever tomatoes are grown. 
                   Bacterial spot causes leaf and fruit spots, which leads to defoliation, sun-scalded fruit, and yield loss. 
                   Due to diversity within the bacterial spot pathogens, the disease can occur at different temperatures and is a threat to tomato production worldwide. 
                   Disease development is favored by temperatures of 75 to 86 ℉ and high precipitation. 
                   In North Carolina, it is more prevalent in seasons with high precipitation and less prevalent during dry years.'''
    elif disease_name == "Tomato-Leaf_Early_blight":
        desc = '''The symptoms of early blight mainly appear on the leaves, stems, petioles, and fruits, and show concentric wheel-pattern spots that are colored dark brown and water-stain-shaped.
                  In humid environments, black molds appear on the disease spots.
                  Spray a fungicide once every 7 days for 3-4 times to effectively control this disease.'''

    elif disease_name == "Tomato-Leaf_healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Tomato-Leaf_Late_blight":
        desc = '''Late blight easily arises in conditions of high temperature and low humidity. 
                  If affected, the petioles and main stem will rot and become blackish brown. 
                  The slightly concave spots begin to spread inward from the leaf tips and margins, looking like white mold when wet and dark brown when dry. 
                  Spray a fungicide once every 7 days 2-3 times to control this disease.'''
    elif disease_name == "Tomato-Leaf_Tomato_Yellow_Leaf_Curl_Virus":
        desc = '''Typical symptoms for this disease in tomato are yellow (chlorotic) leaf edges, upward leaf cupping, leaf mottling, reduced leaf size, and flower drop. 
                  TYLCV can have a severe impact on tomato production. 
                  Plants infected at an early stage won't bear fruit and their growth will be severely stunted.'''
    elif disease_name == "Not Recognized":
        desc = '''None'''

    else:
        desc = "None"

    return desc

# Remedy_Details


def remedy_detail(disease_name):
    if disease_name == "Cassava_Bacterial_Blight":
        desc = '''Pruning or total extirpation of infected plant tissue
        Weed removal
        Use of certified seeds
        Bacterial analysis of stem cuttings
        Crop rotation are used the most to limit the disease presence in the field.'''

    elif disease_name == "Cassava_Brown_Streak_Virus_Disease":
        desc = '''> Make sure to use virus-free planting material from certified sources.
> Grow varieties that have been proven to be resistant or tolerant to
CBSV.
> Monitor the field weekly for the first 3 months of manioc growth and
remove diseased or deformed plants.
>-Destroy the rogued plants immediately by burning or deep burying.
> Keep the fields weed-free to avoid alternative hosts of insects that
transfer CBSV.
> Disinfect agricultural tools when working between different fields.
> Do not transport cuttings to new fields or areas.'''

    elif disease_name == "Cassava_Green_Mite":
        desc = '''> Use varieties with good tolerance to the mite.
> Only use certified cuttings for planting.
> Plant early at the start of the rainy season, to ensure sufficient plant
resistance when the dry season begins.
> Intercrop with pigeon pea, if possible in double or triple rows, and
avoid slanted planting.
> Regularly monitor the manioc field for symptoms or sightings of the
mite.
> Avoid transportation of infested material to markets or other fields
as this is the main cause of dispersal.'''

    elif disease_name == "Cassava_healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Cassava_Mosaic_Disease":
        desc = '''> Only use certified seeds from a certified source.
> Cultivate a resistant manioc variety, if available on the market.
> Maintain all tools involved in manioc cultivation clean and disinfect
them is possible.
→ Use uniform and dense manioc stands rather than irregular widely
spaced ones.
> Intercropping with species such as banana, sweet potato, cereals
and legumes decreases whitefly population
> Preferably plant manioc in well nurtured soil and fertilize accordingly.
> Remove all infected manjoc plants from the field and destroy (burn
or bury) them in distance'''

    elif disease_name == "Corn_(maize)___Northern_Leaf_Blight":
        desc = '''> Plant resistant varieties if available in your area.
        > Plant different varieties of maize to avoid monocultures.
> Make sure to keep field clean.
> Rotate with non-host crops.
> Plow deep to bury crop residues in the soil.
> Plan a fallow after the harvest.'''

    elif disease_name == "Corn_(maize)___Common_rust":
        desc = '''> Plant resistant varieties available locally.
> Plant early to avoid optimal conditions for infection.
> Use shorter season varieties that mature earlier.
> Monitor your crop regularly for signs of the disease, even more so
during overcast weather.
> Ensure balanced fertilization with split applications of nitrogen.
> Plan a crop rotation with non-susceptible crops.'''

    elif disease_name == "Corn_(maize)_Gray_Leaf_Spot":
        desc = '''> Plant resistant varieties if available in your area.
> Plant late to avoid adverse conditions for plants.
> Keep up good ventilation by widening the space between plants.
> Plow deep and bury all plant residues after harvest.
> Plan long-term crop rotations with non-host plants.'''

    elif disease_name == "Corn_(maize)___healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Tomato-Leaf___Bacterial_spot":
        desc = '''A plant with bacterial spot cannot be cured. 
                  Remove symptomatic plants from the field or greenhouse to prevent the spread of bacteria to healthy plants. 
                  Burn, bury or hot compost the affected plants and DO NOT eat symptomatic fruit.'''
    elif disease_name == "Tomato-Leaf_Early_blight":
        desc = '''1}Rotate Your Crops.
                  2}Purge Nightshades and Volunteer Tomato Plants.
                  3}Keep Your Plants Dry.
                  4}Stake Your Plants.
                  5}Remove Infected Plants.'''
    elif disease_name == "Tomato-Leaf_healthy":
        desc = '''Keep nurturing your plant in proper manner as you are doing'''

    elif disease_name == "Tomato-Leaf_Late_blight":
        desc = '''If you notice late blight early on in the disease's progression, 
                  treat the plant with one of these recommended fungicide options: Copper-based fungicides – Use a copper-based fungicide (mix 2 ounces of fungicide with a gallon of water) every 6 or 7 days following a watering or heavy rain.'''

    elif disease_name == "Tomato-Leaf_Tomato_Yellow_Leaf_Curl_Virus":
        desc = '''The key to managing tomato leaf curl is through prevention. Plant only pest and disease-resistant varieties. 
                  Also, protect garden plants from possible whitefly infestations by adding floating row covers and keep the area free of weeds, which often attract these pests.'''

    elif disease_name == "Not Recognized":
        desc = '''None'''

    else:
        desc = "None"

    return desc


# Plant name
def plant_name(disease_name):

    if disease_name == "Not Recognized":
        return "Not Identified"
    else:
        return disease_name


# scientific name
def scific_name(disease_name):

    if disease_name == "Cassava_Bacterial_Blight":
        return "Manihot esculenta"

    elif disease_name == "Cassava_Brown_Streak_Virus_Disease":
        return "Manihot esculenta"
    elif disease_name == "Cassava_Green_Mite":
        return "Manihot esculenta"
    elif disease_name == "Cassava_healthy":
        return "Manihot esculenta"
    elif disease_name == "Cassava_Mosaic_Disease":
        return "Manihot esculenta"
    elif disease_name == "Corn_(maize)___Northern_Leaf_Blight":
        return "Zea mays"
    elif disease_name == "Corn_(maize)___Common_rust":
        return "Zea mays"
    elif disease_name == "Corn_(maize)_Gray_Leaf_Spot":
        return "Zea mays"
    elif disease_name == "Corn_(maize)___healthy":
        return "Zea mays"

    elif disease_name == "Tomato-Leaf___Bacterial_spot":
        return "Solanum lycopersicum"
    elif disease_name == "Tomato-Leaf_Early_blight":
        return "Solanum lycopersicum"
    elif disease_name == "Tomato-Leaf_healthy":
        return "Solanum lycopersicum"
    elif disease_name == "Tomato-Leaf_Late_blight":
        return "Solanum lycopersicum"
    elif disease_name == "Tomato-Leaf_Tomato_Yellow_Leaf_Curl_Virus":
        return "Solanum lycopersicum"

    else:
        return "None"


# Tomato desc
def tomato_desc(disease_name):

    if disease_name == "Cassava_Bacterial_Blight":
        return '''Cassava is a root vegetable. It is the underground part of the cassava shrub, which has the Latin name Manihot esculenta. Like potatoes and yams, it is a tuber crop. Cassava roots have a similar shape to sweet potatoes.'''

    elif disease_name == "Cassava_Brown_Streak_Virus_Disease":
        return '''Cassava is a root vegetable. It is the underground part of the cassava shrub, which has the Latin name Manihot esculenta. Like potatoes and yams, it is a tuber crop. Cassava roots have a similar shape to sweet potatoes.'''
    elif disease_name == "Cassava_Green_Mite":
        return '''Cassava is a root vegetable. It is the underground part of the cassava shrub, which has the Latin name Manihot esculenta. Like potatoes and yams, it is a tuber crop. Cassava roots have a similar shape to sweet potatoes.'''
    elif disease_name == "Cassava_healthy":
        return '''Cassava is a root vegetable. It is the underground part of the cassava shrub, which has the Latin name Manihot esculenta. Like potatoes and yams, it is a tuber crop. Cassava roots have a similar shape to sweet potatoes.'''
    elif disease_name == "Cassava_Mosaic_Disease":
        return '''Cassava is a root vegetable. It is the underground part of the cassava shrub, which has the Latin name Manihot esculenta. Like potatoes and yams, it is a tuber crop. Cassava roots have a similar shape to sweet potatoes.'''
    elif disease_name == "Corn_(maize)___Northern_Leaf_Blight":
        return '''Corn, (Zea mays), also called Indian corn or maize, cereal plant of the grass family (Poaceae) and its edible grain. The domesticated crop originated in the Americas and is one of the most widely distributed of the world’s food crops. Corn is used as livestock feed, as human food, as biofuel, and as raw material in industry.

'''
    elif disease_name == "Corn_(maize)___Common_rust":
        return '''Corn, (Zea mays), also called Indian corn or maize, cereal plant of the grass family (Poaceae) and its edible grain. The domesticated crop originated in the Americas and is one of the most widely distributed of the world’s food crops. Corn is used as livestock feed, as human food, as biofuel, and as raw material in industry.

'''
    elif disease_name == "Corn_(maize)_Gray_Leaf_Spot":
        return '''Corn, (Zea mays), also called Indian corn or maize, cereal plant of the grass family (Poaceae) and its edible grain. The domesticated crop originated in the Americas and is one of the most widely distributed of the world’s food crops. Corn is used as livestock feed, as human food, as biofuel, and as raw material in industry.

'''
    elif disease_name == "Corn_(maize)___healthy":
        return '''Corn, (Zea mays), also called Indian corn or maize, cereal plant of the grass family (Poaceae) and its edible grain. The domesticated crop originated in the Americas and is one of the most widely distributed of the world’s food crops. Corn is used as livestock feed, as human food, as biofuel, and as raw material in industry.

'''

    elif disease_name == "Tomato-Leaf___Bacterial_spot":
        return '''Tomato is an annual or perennial
        herbaceous vine native to Central and South America that produces a
        large, juicy, edible fruit known as tomato. Today there are over
        10000 cultivated varieties. Although tomato is the world’s most
        popular vegetable, botanically it is a fruit.'''
    elif disease_name == "Tomato-Leaf_Early_blight":
        return '''Tomato is an annual or perennial
            herbaceous vine native to Central and South America that produces a
            large, juicy, edible fruit known as tomato. Today there are over
            10000 cultivated varieties. Although tomato is the world’s most
            popular vegetable, botanically it is a fruit.'''
    elif disease_name == "Tomato-Leaf_healthy":
        return '''Tomato is an annual or perennial
            herbaceous vine native to Central and South America that produces a
            large, juicy, edible fruit known as tomato. Today there are over
            10000 cultivated varieties. Although tomato is the world’s most
            popular vegetable, botanically it is a fruit.'''
    elif disease_name == "Tomato-Leaf_Late_blight":
        return '''Tomato is an annual or perennial
            herbaceous vine native to Central and South America that produces a
            large, juicy, edible fruit known as tomato. Today there are over
            10000 cultivated varieties. Although tomato is the world’s most
            popular vegetable, botanically it is a fruit.'''
    elif disease_name == "Tomato-Leaf_Tomato_Yellow_Leaf_Curl_Virus":
        return '''Tomato is an annual or perennial
            herbaceous vine native to Central and South America that produces a
            large, juicy, edible fruit known as tomato. Today there are over
            10000 cultivated varieties. Although tomato is the world’s most
            popular vegetable, botanically it is a fruit.'''

    else:
        return "None"
