import os 
import pandas as pd 
import streamlit as st
import base64
import ast
from auxiliaries import parse_cell, cell_check, validate_keys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import datetime
import numpy as np


TOPICS_DICT = {
        "Armed Conflict": ["armed", "bomb", "war", "conflict", "battle", "military", "guerrilla", "insurgent", "bomba", "guerra", "conflicto", "batalla", "militar", 'humanitarian law', 'gaza'],
        "Arms Trade": ["arms trade", "arm trade", "weapon", "gun", "firearm", "missile", "explosive", "munition", "comercio de armas", "arma de fuego", "misil", "explosivo", "municion"],
        "Asylum": ["asylum", "forced migration", "refugee", "displaced", "deport", "immigration", "asilo", "migración", "refugiado", "desplazad", "deporta", "inmigración"],
        "Business and Human Rights": ['Business',"corporate", "vaccine", "labor rights", "working conditions", "fair trade", "corporativo", "vacuna", "derechos laborales", "condiciones de trabajo"],
        "Censorship and Freedom of Expression": ["censor", "rule of law", "freedom of expression", "free speech", "press freedom","Freedom of belief", "protest", "censura", "freedom of speech", "libertad de expresión", "libertad de prensa", "protesta"],
        "Children": ["children","family","kids","primary education", "Primary school", "PUNCH AND JUDY","child","jolie", "parent", "Passport", "First Steps", "cuento","toddler", "infant","infancia","niña", "familia", "educación primaria", "escuela primaria", "padre", "Pasaporte","Primeros Pasos", "niño", "infante"],
        "Climate Change": ["Climate", "global warming", "environment", "sustainability", "carbon", "emissions", "pollution", "renewable energy", "Climatico", "calentamiento global", "medio ambiente", "sustenibilidad", "carbono", "emisiones", "contaminación", "energía renovable"],
        "Corporate Accountability": ["corporate", "corporate responsibility", "business ethics", "corporativ", "empresa"],
        "COVID-19": ["vaccine", "covid", "coronavirus", "pandemic", "quarantine", "social distancing", "vacuna", "covid", "coronavirus", "pandemia", "cuarentena", "distanciamiento"],
        "Death in Custody": ["prison death", "jail death", "incarceration", "custodial death", "muerte en prisión", "muerte en la cárcel", "encarcelamiento", "muerte bajo custodia"],
        "Death Penalty": ["Death Penalty", "Death row", "execution", "capital punishment", "hanging", "hanged", "pena de muerte", "ejecuci", "castigo capital", "horca"],
        "Detention": ["Detained", "detention", "Detainee", "imprisonment", "incarceration", "jail", "prison", "custody", "detención", "detenid", "encarcelamiento", "prisión", "custodi"],
        "Courts": ["court","judiciary", "FAIR TRIAL", "judge", "tribunal", "corte", "poder judicial", "juez", "tribunal"],
        "Disability Rights": ["disabled", "disabilit", "lenguaje de señas", "special needs","discapacitad", "necesidades especiales"],
        "Disappearances": ["Disappearance", "missing", "abducted", "kidnapped", "desaparición", "desaparecid", "secuestr"],
        "Discrimination": ["Discrimination","odio","bullying", "elderly","apartheid", "equality", "prejudice", "bias", "inequality", "stereotyp", "racism", "sexism", "homophobia", "discriminación","odio", "hate","apartheid", "igualdad", "prejuicio", "sesgo", "desigualdad", "estereotip", "racismo", "sexismo", "homofobia"],
        "Domestic Violence": ["Domestic Violence", "abuse", "spousal abuse", "battered","Collective rights", "home violence", "violencia doméstica", "abuso", "maltrato", "machist"],
        "Economic, Social and Cultural Rights": ['Economic, Social and Cultural Rights', "economic rights","ECHR ", "ESCR", "economic", "cultural rights", "poverty", "income inequality", "economic justice", "social justice", "derechos económicos", 
                                                 "ECONOMi", "pobreza", "pobre", "justicia económica", 'development', "socio economic", "socioeconomic", "socio-economic", "worker"],
        "EU": ["the EU", "european union", "europe", "european commission", "european parliament", "brexit", "la UE", "unión europea", "europa", "comisión europea", "parlamento europeo", "brexit"],
        "Freedom of Association": ["protest", "repression", "freedom of assembly","right to assembly", "tear gas","Freedom of Association", "trade union", "unions", "right to organize",  "protesta", "represión", "gas lacrimógeno","Libertad de Asociación", "sindicatos", "derecho a organizarse", "marcha"],
        "Freedom of Movement": ["Freedom of Movement", "travel", "migration", "checkpoint", "Libertad de Movimiento", "libertad de transito" "viaj"],
        "Human Rights Defenders and Activists": ["defens","defend","brave"," bold", "COURAGE", "Activism","activist","Save a Life","Mardini", "w4r","write for","write 4", "Marathon", "defensor","valiente", "CORAJE", "Activismo", "activista", "Escribe por los Derechos", "Maratón"],
        "Write for Rights": ['w4r', "Writing for rights","write for","write 4", "Marathon","Escribe por los Derechos", "Maratón", 'letter writ'],
        "Activism Skills": ['fundrais', 'Activism Skills', 'skill' ,'start a local', 'start a youth', 'organize an event', 'organize events', 'Brand', 'treasur', 'local group', 'youth group','host a'],
        "Indigenous People": ["indigenous", "native", "aboriginal", "native american", "first nations", "tribal", "tribe", "indígena", "originari", "aborigen", "nativo", "tribu"],
        "Internally Displaced People": ["Internally Displaced People", "displacement", "forced migration", "Personas Desplazadas Internamente", "desplazamiento", "migración forzada"],
        "Intro to Human Rights": ['Introduction to amnesty', "treaty", "treaties", 'Intro to amnesty', "Basic knowledge about", 'beginner', 'first step', 'Introduction to human rights', 'Intro to human rights','UDHR', 'universal declaration', 'passport'],
        "Killings and Disappearances": ["Disappearance", "killing", "extrajudicial", "murder", "homicide", "assassination", "genocide", "desaparición", "asesinato", "extrajudicial", "homicidio", "asesinato", "genocidio"],
        "LGBTI Rights": ["LGBT", "queer", "gay", "LGBI","LGTBI","lesbian", "pride", 'rainbow','transphobi',"trans people","Equal Marriage", "intersex", "homosexual", "transgender","MiNombreDebeSerLegal","Soy Real", "bisexual","trans rights", "gender identity", "LGBT ", "gay", "lesbiana", "intersex", "transgénero", "bisexual","personas trans","ser trans ","transexual", "diversxs","los trans","identidad de género"],
        "Land and Human Rights":['land','urban', 'rural', 'territor'],
        "Maternal Health and Reproductive Rights": ["maternal", "abortion", "reproductive", "pregnancy", "maternity", "childbirth", "family planning", "contraception", "maternal", "aborto", "reproductiv", "embarazo", "maternidad", "parto","anticonceptiv"],
        "Migrants": ["refugee", "People on the move", "asylum", "migration", "migrant", "border", "expatriate", "refugiado", "asilo", "migración", "frontera", "expatriado"],
        "Poverty": ["poverty", "dignity", "the poor", "homelessness", "food insecurity", "inequality", "underprivileged", "lack of resources", "pobreza", "los pobres", "sin hogar", "inseguridad alimentaria", "desigualdad", "desfavorecido", "escasez de recursos","falta de recursos", "dignidad"],
        "Prisoners of Conscience": ["Prisoners of Conscience", "Prisoner of Conscience", "political prisoner", "Prisioneros de Conciencia", "Prisionero de Conciencia", "presos políticos","preso político"],
        "Protests and Demonstrations": ["Protest", "tear gas", "repression", "riot", "march", "demo", "Protesta", "gas lacrimógeno", "represión",  "marcha"],
        "Police and Human Rights": ['police', 'policing', 'law enforcement', "tear gas","gas lacrimógeno", "represión","tear gas","rubber bullets", "state repression","police brutality","use of force","excessive force","arrests", "racial profiling","firearms","state violence", "public safety","civil disobedience"],
        "Racial Discrimination": ["racism", "racist", "racial", "ethnic", "segregation", "racial justice", "racial equality", "racial bias", "racismo", "racista", "racial", "segregación", "justicia racial", "igualdad racial", "sesgo racial"],
        "People Trafficking": ["Trafficking", "slavery", "Human smuggling", "Forced prostitution"],
        "Refugees": ["refug", "asylum", "forced migration", "Mardini","displaced", "stateless", "asylum seeker", "migración forzada", "desplazad", "refugiad", "asilo"],
        "Right to Food": ["hunger", "food security", "malnutrition", "starvation","Right to Food", "hambre", "seguridad alimentaria", "desnutrición", "inanicción","Derecho a la Alimentación"],
        "Right to Health": ["vaccine", "covid", "enferm","coronavirus", "pandemic", "health", "healthcare", "medical care", "public health", "health rights", "vacuna", "pandemia", "salud", "atención médica", "cuidado médico"],
        "Right to Water": ["Water","sanitation", "Agua","saneamiento"],
        "Sexual Rights": ["Sexual", "gender","itsmybody","ESImportante","StandByMe", "stand by me", "esmicuerp", "mi cuerp","cuerpo","cuerpa" ,"sex education","MY BODY", "consent", "sexuality", "sex education","diversxs", "Sexual", "MI CUERPO", "consentimiento", "sexualidad", " esi ","educación sexual","diversxs", "derechos sexuales"],
        "Sexual Violence": ["Sexual Violence","violencia en el Noviazgo","Noviazgo sin violencia", "Violencia de género","consent", "rape", "sexual abuse", "sexual assault", "molestation", "sexual harassment", "me too","gender based violence", "gender violence", "Violencia Sexual", "consentimiento", "violación", "abuso sexual","machista", "ni una menos","acoso sexual", "femicid"],
        "Slums and the Right to Housing": ["slum", "housing", "homelessness", "affordable housing","villas", "eviction","desalojo","sin hogar", "vivienda", " precari"],
        "Technology and Human Rights": ["surveillance", 'technology', "digital","SNOWDEN","google","facebook","scan","cyber", "biometric","face recognition","facial recognition", "pegasus", "spy", "technolog", "internet freedom", "privacy", "data protection", "artificial intelligence", "algorithm", "vigilancia", "biométrico","reconocimiento facial", "espía", "tecnología", "acceso a internet",
                                        "privacidad", "usuario","protección de los usuarios", "inteligencia artificial", "algoritmo"],
        "Torture and other ill-treatment": ["torture", "tortura", "guantanamo"],
        "UN": ["united nations", "united nations general assembly","un security council", "un human rights council","world health organization", "naciones unidas", "la onu ", "asamblea general de las naciones unidas", "consejo de seguridad de la onu", "consejo de derechos humanos de la onu", "organización mundial de la salud", "las naciones unidas"],
        "Universal Declaration of Human Rights": ['UDHR',"Universal Declaration","Declaration of Human Rights", 'passport',"Declaración Universal",],
        "Unlawful Detention": ["Detained", "detention", "Detainee", "arrest", "imprisonment", "incarceration", "custody", "detenid", "detención", "apresado", "en prisión", "arresto", "encarcelamiento"],
        "Unlawful Killings": ["killing", "murder", "assassination", "homicide", "asesinato", "homicidio"],
        "Women's Rights": ["women","ellas", "woman", "girl", "abortion", "glass","gender equality", "me too", "mujeres", "mujer", "niña", "aborto","madre", "maternal", "feminist", "igualdad de género"],
        "Youth and Human Rights": ["youth", "Secondary Education", "Secondary school","young","words that burn", "student", "poem", "poetry", "poetic", "young people", "adolescents", "teenagers", "students", "youth activism", "gen z", "generación z","Educación Secundaria", "Escuela Secundaria","joven", "jóvenes", "adolescentes", "estudiantes", "juvenil"],

'Human Rights at School':['Human Rights at School', 'school','escuela', 'schule','colegio', "Schüler","professeur",'student','secondary', 'primary','secundaria', 'primaria', 'kindergarden', 'aula','classroom', "escola", "aluno", 
                          'profesores', 'Friendly School',"studentu", 'friendly school','reading rebel', 'in class', 'école',],
# Countries:

   "Afghanistan": ["Afghanistan", "Afghan", "Kabul"],
    "Africa": ["Africa"],
    "Albania": ["Albania", "Albanian", "Tirana"],
    "Algeria": ["Algeria", "Algerian", "Algiers"],
    "Andorra": ["Andorra", "Andorran", "Andorra la Vella"],
    "Angola": ["Angola", "Angolan", "Luanda"],
    "Argentina": ["Argentina", "Argentinian", "Buenos Aires"],
    "Armenia": ["Armenia", "Armenian", "Yerevan"],
    "Australia": ["Australia", "Australian", "Canberra"],
    "Austria": ["Austria", "Austrian", "Vienna"],
    "Azerbaijan": ["Azerbaijan", "Azerbaijani", "Baku"],
    "Bahrain": ["Bahrain", "Bahraini", "Manama"],
    "Bangladesh": ["Bangladesh", "Bangladeshi", "Dhaka"],
    "Belarus": ["Belarus", "Belarusian", "Minsk"],
    "Belgium": ["Belgium", "Belgian", "Brussels"],
    "Benin": ["Benin", "Beninese", "Porto-Novo"],
    "Bolivia": ["Bolivia", "Bolivian", "La Paz", "Sucre"],
    "Botswana": ["Botswana", "Motswana", "Gaborone"],
    "Brazil": ["Brazil", "Brazilian", "Brasilia"],
    "Bulgaria": ["Bulgaria", "Bulgarian", "Sofia"],
    "Burkina Faso": ["Burkina Faso", "Burkinabe", "Ouagadougou"],
    "Burundi": ["Burundi", "Burundian", "Gitega"],
    "Cambodia": ["Cambodia", "Cambodian", "Phnom Penh"],
    "Cameroon": ["Cameroon", "Cameroonian", "Yaounde"],
    "Canada": ["Canada", "Canadian", "Ottawa"],
    "Chad": ["Chad", "Chadian", "N'Djamena"],
    "Chile": ["Chile", "Chilean", "Santiago"],
    "China": ["China", "Chinese", "Beijing"],
    "Colombia": ["Colombia", "Colombian", "Bogota"],
    "Congo": ["Congo", "Congolese", "Kinshasa"],
    "Côte d'Ivoire": ["Côte d'Ivoire", "Ivorian", "Yamoussoukro", "Abidjan"],
    "Croatia": ["Croatia", "Croatian", "Zagreb"],
    "Cuba": ["Cuba", "Cuban", "Havana"],
    "Cyprus": ["Cyprus", "Cypriot", "Nicosia"],
    "Czech Republic": ["Czech Republic", "Czechia","Czech", "Prague"],
    "Democratic Republic of the Congo": ["Democratic Republic of the Congo, Congo", "Kinshasa"],
    "Denmark": ["Denmark", "Danish", "Copenhagen"],
    "Dominican Republic": ["Dominican Republic", "Dominican", "Santo Domingo"],
    "Ecuador": ["Ecuador", "Ecuadorian", "Quito"],
    "Egypt": ["Egypt", "Egyptian", "Cairo"],
    "El Salvador": ["El Salvador", "Salvadorian", "San Salvador"],
    "Equatorial Guinea": ["Equatorial Guinea", "Equatorial Guinean", "Malabo"],
    "Eritrea": ["Eritrea", "Eritrean", "Asmara"],
    "Estonia": ["Estonia", "Estonian", "Tallinn"],
    "Eswatini": ["Eswatini", "Swazi", "Mbabane", "Lobamba"],
    "Ethiopia": ["Ethiopia", "Ethiopian", "Addis Ababa"],
    "Fiji": ["Fiji", "Fijian", "Suva"],
    "Finland": ["Finland", "Finnish", "Helsinki"],
    "France": ["France", "French", "Paris"],
    "Gambia": ["Gambia", "Gambian", "Banjul"],
    "Georgia": ["Georgia", "Georgian", "Tbilisi"],
    "Germany": ["Germany", "German", "Berlin"],
    "Ghana": ["Ghana", "Ghanaian", "Accra"],
    "Greece": ["Greece", "Greek", "Athens"],
    "Guatemala": ["Guatemala", "Guatemalan", "Guatemala City"],
    "Guinea": ["Guinea", "Guinean", "Conakry"],
    "Haiti": ["Haiti", "Haitian", "Port-au-Prince"],
    "Honduras": ["Honduras", "Honduran", "Tegucigalpa"],
    "Hungary": ["Hungary", "Hungarian", "Budapest"],
    "Iceland": ["Iceland", "Icelandic", "Reykjavik"],
    "India": ["India", "Indian", "New Delhi"],
    "Indonesia": ["Indonesia", "Indonesian", "Jakarta"],
    "Iran": ["Iran", "Iranian", "Tehran"],
    "Iraq": ["Iraq", "Iraqi", "Baghdad"],
    "Ireland": ["Ireland", "Irish", "Dublin"],
    "Israel and Occupied Palestinian Territories": ["Israel and Occupied Palestinian Territories", "Palestine", "OPT", "Palestinian", "Israeli", "Ramallah","Sheikh Jarrah", "West Bank", "Gaza", "Israel", "Tel aviv", "Jerusalem", "settlements"],
    "Italy": ["Italy", "Italian", "Rome"],
    "Japan": ["Japan", "Japanese", "Tokyo"],
    "Jordan": ["Jordan", "Jordanian", "Amman"],
    "Kazakhstan": ["Kazakhstan", "Kazakh", "Nur-Sultan"],
    "Kenya": ["Kenya", "Kenyan", "Nairobi"],
    "Kosovo": ["Kosovo", "Kosovan", "Pristina"],
    "Kuwait": ["Kuwait", "Kuwaiti", "Kuwait City"],
    "Kyrgyzstan": ["Kyrgyzstan", "Kyrgyz", "Bishkek"],
    "Laos": ["Laos", "Laotian", "Vientiane"],
    "Latvia": ["Latvia", "Latvian", "Riga"],
    "Lebanon": ["Lebanon", "Lebanese", "Beirut"],
    "Lesotho": ["Lesotho", "Basotho", "Maseru"],
    "Libya": ["Libya", "Libyan", "Tripoli"],
    "Lithuania": ["Lithuania", "Lithuanian", "Vilnius"],
    "Madagascar": ["Madagascar", "Malagasy", "Antananarivo"],
    "Malawi": ["Malawi", "Malawian", "Lilongwe"],
    "Malaysia": ["Malaysia", "Malaysian", "Kuala Lumpur"],
    "Maldives": ["Maldives", "Maldivian", "Male"],
    "Mali": ["Mali", "Malian", "Bamako"],
    "Morocco": ["MOROCCO"],
    "Uruguay":["URUGUAY"],
    "Zimbabwe": ["ZIMBABWE"],
    "Malta": ["Malta", "Maltese", "Valletta"],
    "Mexico": ["Mexico", "Mexican", "Mexico City"],
    "Middle East and North Africa": ["Middle East and North Africa", "MENA"],
    "Moldova": ["Moldova", "Moldovan", "Chisinau"],
    "Mongolia": ["Mongolia", "Mongolian", "Ulaanbaatar"],
    "Montenegro": ["Montenegro", "Montenegrin", "Podgorica"],
    "Mozambique": ["Mozambique", "Mozambican", "Maputo"],
    "Myanmar": ["Myanmar", "Burmese", "Naypyidaw"],
    "Namibia": ["Namibia", "Namibian", "Windhoek"],
    "Nepal": ["Nepal", "Nepali", "Kathmandu"],
    "Netherlands": ["Netherlands", "Dutch", "Amsterdam", "The Hague"],
    "New Zealand": ["New Zealand", "New Zealander", "Kiwi", "Wellington"],
    "Nicaragua": ["Nicaragua", "Nicaraguan", "Managua"],
    "Niger": ["Niger", "Nigerien", "Niamey"],
    "Nigeria": ["Nigeria", "Nigerian", "Abuja"],
    "North America": ["North America"],
    "North Korea": ["North Korea", "North Korean", "Pyongyang"],
    "North Macedonia": ["North Macedonia", "Macedonian", "Skopje"],
    "Norway": ["Norway", "Norwegian", "Oslo"],
    "Oman": ["Oman", "Omani", "Muscat"],
    "Pakistan": ["Pakistan", "Pakistani", "Islamabad"],
    "Palestine": ["Palestine", "Palestinian", "Ramallah", "Gaza"],
    "Papua New Guinea": ["Papua New Guinea", "Papuan", "Port Moresby"],
    "Paraguay": ["Paraguay", "Paraguayan", "Asunción"],
    "Peru": ["Peru", "Peruvian", "Lima"],
    "Philippines": ["Philippines", "Philippine", "Filipino", "Manila"],
    "Poland": ["Poland", "Polish", "Warsaw"],
    "Portugal": ["Portugal", "Portuguese", "Lisbon"],
    "Puerto Rico": ["Puerto Rico", "Puerto Rican", "San Juan"],
    "Qatar": ["Qatar", "Qatari", "Doha"],
    "Romania": ["Romania", "Romanian", "Bucharest"],
    "Russia": ["Russia", "Russian", "Putin", "Moscow"],
    "Rwanda": ["Rwanda", "Rwandan", "Kigali"],
    "Saudi Arabia": ["Saudi Arabia", "Saudi", "Saudia", "Riyadh"],
    "Senegal": ["Senegal", "Senegalese", "Dakar"],
    "Serbia": ["Serbia", "Serbian", "Belgrade"],
    "Sierra Leone": ["Sierra Leone", "Sierra Leonean", "Freetown"],
    "Singapore": ["Singapore", "Singaporean"],
    "Slovakia": ["Slovakia", "Slovak", "Bratislava"],
    "Slovenia": ["Slovenia", "Slovenian", "Ljubljana"],
    "Somalia": ["Somalia", "Somali", "Mogadishu"],
    "South Africa": ["South Africa", "South African", "Pretoria", "Cape Town", "Bloemfontein"],
    "South America": ["South America"],
    "South Asia": ["South Asia"],
    "South Korea": ["South Korea", "South Korean", "Seoul"],
    "South Sudan": ["South Sudan", "South Sudanese", "Juba"],
    "Spain": ["Spain", "Spanish", "Madrid"],
    "Sri Lanka": ["Sri Lanka", "Sri Lankan", "Colombo", "Sri Jayawardenepura Kotte"],
    "Sudan": ["Sudan", "Sudanese", "Khartoum"],
    "Sweden": ["Sweden", "Swedish", "Stockholm"],
    "Switzerland": ["Switzerland", "Swiss", "Bern"],
    "Syria": ["Syria", "Syrian", "Damascus"],
    "Taiwan": ["Taiwan", "Taiwanese", "Taipei"],
    "Tajikistan": ["Tajikistan", "Tajik", "Dushanbe"],
    "Tanzania": ["Tanzania", "Tanzanian", "Dodoma"],
    "Thailand": ["Thailand", "Thai", "Bangkok"],
    "Togo": ["Togo", "Togolese", "Lomé"],
    "Trinidad and Tobago": ["Tobago", "Trinidadian", "Tobagonian", "Port of Spain"],
    "Tunisia": ["Tunisia", "Tunisian", "Tunis", "Tunez"],
    "Turkiye": ["Türkiye", "Turkiye", "Turkey", "Turkish", "Erdogan", "Ankara"],
    "Turkmenistan": ["Turkmenistan", "Turkmen", "Ashgabat"],
    "Uganda": ["Ugand", "Kampala"],
    "Ukraine": ["Ukraine", "Ukranian","Ukrainian", "Kyiv"],
    "United Arab Emirates": ["United Arab Emirates", "UAE", "Emirati", "Abu Dhabi"],
    "United Kingdom": ["United Kingdom", "the uk", "British",  " uk ", "london"],
    "United States of America": ["the US ", "North America", "united states", "biden", "Washington", "D.C.", "USA "]
}

EDU_CATEGORIES = {
        'Online courses': ['academy', 'e-learning', 'e learning', 'elearning', 'online course',
                    'module', 'academia', 'e-learning', "MOOC", 'e learning',
                    'elearning', 'curso', 'new course'],
        'Manuals': ['manual', 'guide', 'workbook', 'booklet', 'guidebook', 'handbook',
                    'compendium', 'MATERIAL ON ', 'MATERIAL for ', 'first step',
                    'Handbook', 'Curriculum', 'toolkit', 'pack', 'tool-kit',
                    "TEACHING RECOMMENDATION",'tool kit', "materiales de",
                    "Learning materials","template", 'Bite Size',
                    'Bitesize', 'Booklet', 'manual', 'guia', 'guía', 'compendio',
                    'toolkit', 'tool kit', 'material para', 'material'
                    'sobre', 'Human rights in the classroom', 'pdf', 'Educational material', 'teaching unit'],
        'Art and Human Rights': ['arts', 'Art and Human Rights','artist','art and','exhibition','theater',
                                 'poster','photograph','music', 'concert'],
        'Classroom Activity': ['actividades','Classroom Activit', 'para el aula', 'actividad','activity','Session plan',
                               "game","juego", 'interactive', 'interactivo', 'classroom', 'class room','kahoot', 
                               'quiz', 'debate','discussion', 'puzzle','materiel-pedagogique','leaflet', 'slides',
                    'PowerPoint','print', 'passport','Presentation on', 'In-class'],
        'Books and Human Rights': ['books', 'reading', 'jolie', 'reader', 'book ', 'poet', 'poem', 'fiction', 'Books and Human Rights'],
        'Video': ['video', 'youtube', 'youtu.be', 'vimeo', 'film', 'Screening', 'movie', 'trailer',
                  'documentary', 'documentaries', 'multimedia'],
        'Movies and Documentaries': ['documentary', 'Movies and Documentaries', 'documentaries', 'film', 'Screening', 'movie', 'trailer', 'pelicula', 'película'],
        'Podcast': ['audio', 'podcast', 'radio', 'escuchar', 'spotify'],
        'Get Involved': ['Club', 'get involved',
                         'participate', 'contest', 'competition',
                         'register',"Join", "tour", "festival",'Inscription',
                         'Registration', 'sign up', 'sign-up', 'your school',
                         'como participar', 'cómo participar', 'tu escuela',
                         'tu colegio', 'colegio amigo', "your school",
                         'Request'],

        'News and more': ['news', 'blog', 'event', 'conference', 'job search',
                          'job offer', 'vacancy', 'Jolie', 'camp ', 'Human Libraries',
                          'launches', 'Book review', 'evento', 'vacante', 'laboral',
                          'puesto de trabajo', 'puesto laboral', 'interview', 'award', 'prize', 'announce'],
        'Blogs':['blog'],
        'About HRE': ["about hre", 'preguntas', 'questions', 'q&a', 'state of human rights education']
        }
valid_sources = [
    "IS",
    'AI ZIMBABWE',
    'AI HONG KONG',
    "AI ALGERIA",
    "AI ARGENTINA",
    "AI AUSTRALIA",
    "AI AUSTRIA",
    "AI BELGIUM",
    "AI BRAZIL",
    "AI BURKINA FASO",
    "AI CANADA",
    "AI CHILE",
    "AI CZECHIA",
    "AI DENMARK",
    "AI EUROPEAN UNION",
    "AI FINLAND",
    "AI FRANCE",
    "AI GERMANY",
    "AI GHANA",
    "AI GREECE",
    "AI HUNGARY",
    "AI ICELAND",
    "AI INDIA",
    "AI INDONESIA",
    "AI IRELAND",
    "AI ISRAEL",
    "AI ITALY",
    "AI JAPAN",
    "AI KENYA",
    "AI LUXEMBOURG",
    "AI MALAYSIA",
    "AI MALI",
    "AI MEXICO",
    "AI MOLDOVA",
    "AI MONGOLIA",
    "AI MOROCCO",
    "AI NEPAL",
    "AI NETHERLANDS",
    "AI NEW ZEALAND",
    "AI NIGERIA",
    "AI NORWAY",
    "AI PARAGUAY",
    "AI PERU",
    "AI PHILIPPINES",
    "AI POLAND",
    "AI PORTUGAL",
    "AI PUERTO RICO",
    "AI SENEGAL",
    "AI SLOVAKIA",
    "AI SLOVENIA",
    "AI SOUTH AFRICA",
    "AI SOUTH KOREA",
    "AI SPAIN",
    "AI SWEDEN",
    "AI SWITZERLAND",
    "AI TAIWAN",
    "AI THAILAND",
    "AI TOGO",
    "AI TURKEY",
    "AI UK",
    "AI UKRAINE",
    "AI URUGUAY",
    "AI USA",
    "AI VENEZUELA",
]

valid_languages= [
 'ARABIC', 'BANGLA', 'BASQUE', 'BOSNIAN', 'BULGARIAN', 'CATALAN', 'CHINESE', 
 'CZECH', 'DAGBANI', 'DANISH', 'DARI', 'DUTCH', 'ENGLISH', 'EWE', 'FARSI', 
 'FILIPINO', 'FINNISH', 'FRENCH', 'GAELIC', 'GALICIAN', 'GERMAN', 'GREEK', 
 'HAUSA', 'HAITIAN','HEBREW', 'HUNGARIAN', 'ICELANDIC', 'INDONESIAN', 'ITALIAN', 
 'JAPANESE', 'KABYE', 'KAZAKH', 'KOREAN', 'KURDISH', 'KYRGYZ','LUXEMBOURGISH', 'MALAY', 
 'MONGOL', 'MONGOLIAN', 'NEPALI', 'NORWEGIAN', 'PERSIAN', 'POLISH',
 'PORTUGUESE', 'ROMANIAN', 'RUSSIAN', 'SERBIAN', 'SIMPLIFIED CHINESE', 'RUNDI',
 'SLOVAK', 'SLOVENIAN', 'SOUTHERN SOTHO', 'SPANISH', 'SWEDISH', 'THAI', 
 'TRADITIONAL CHINESE', 'TURKISH', 'TWI', 'UKRAINIAN', 'URDU', 'VENDA', 'WELSH'
]

def str_to_list(x):
    return ast.literal_eval(x)

def cell_check_source(x, keys):
    return x not in keys

def cell_check(cell, keys):
    """True if cell has issues"""
    try:
        l = ast.literal_eval(cell)
        return any([y not in keys for y in l])
    except ValueError:
        return True 

def csv_checker(df, column, keys, f = cell_check):
 
    keys = [k.upper() for k in keys]
 
    issues = df[column].apply(lambda x: f(x, keys))
    
    if any(issues):
        index = [index for index, value in enumerate(issues) if value]
        for i in index:
            print(f"Row {i} with content {df[column].iloc[i]} is not a valid category")
        

COUNTRY_NAMES = [
    "Afghanistan", "Africa", "Albania", "Algeria", "Andorra", "Angola", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Belarus", "Belgium", "Benin", "Bolivia", "Botswana",
    "Brazil", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Chad", "Chile", "China",
    "Colombia", "Congo", "Côte d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Democratic Republic of the Congo",
    "Denmark", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
    "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Guatemala",
    "Guinea", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Israel and Occupied Palestinian Territories", "Italy", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kosovo", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Libya", "Lithuania", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Mexico", "Middle East and North Africa", "Moldova", "Mongolia", "Montenegro",
    "Morocco", "Mozambique", "Myanmar", "MOROCCO", "Namibia", "Nepal", "Netherlands", "New Zealand", "Nicaragua",
    "Niger", "Nigeria", "North America", "North Korea", "North Macedonia", "Norway", "Oman", "Pakistan", "Palestine",
    "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Romania",
    "Russia", "Rwanda", "Saudi Arabia", "Senegal", "Serbia", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
    "Somalia", "South Africa", "South America", "South Asia", "South Korea", "South Sudan", "Spain", "Sri Lanka",
    "Sudan", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Togo",
    "Trinidad and Tobago", "Tunisia", "Türkiye", "Turkiye", "Turkmenistan", "Uganda", "Ukraine", "Uruguay","United Arab Emirates",
    "United Kingdom", "United States of America", "Zimbabwe", "EU"
]



#--------------------------------------------- google sheets operations---------------------------------------------------
# Google Sheets Constants
CREDENTIALS_FILE = 'credentials.googlesheets.json.json'
RESOURCE_SPREADSHEET_NAME = 'Users-input-streamlit'
ISSUE_SPREADSHEET_NAME = 'Report-an-issue-streamlit'
SHEET_NAME = 'Sheet1'

# Google Sheets Connection
def connect_to_gsheet(spreadsheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", 
             "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.sheet1  # Access the first sheet directly


# Function to append data to a Google Sheet
def add_to_sheet(spreadsheet_name, data_row):
    sheet = connect_to_gsheet(spreadsheet_name)  # Connect to the spreadsheet
    sheet.append_row(data_row)  # Append the row

#--------------------------------------------------------------                  -------------------------------------------------------------


def set_bg_hack(main_bg):
    '''
    Unpack an image from root folder and set as bg.
    '''
    # set bg name
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
             overflow: hidden
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
    
def add_country_topic_column(df):
    # Convert all tags and country names to uppercase for case-insensitive comparison
    df['Tags'] = df['Tags'].apply(lambda tags: [tag.upper() for tag in tags])
    country_names_upper = [name.upper() for name in COUNTRY_NAMES]

    # Add a new column 'Country_Topic' and populate it based on matching tags with COUNTRY_NAMES
    df['Country_Topic'] = df['Tags'].apply(lambda tags: [tag for tag in tags if tag in country_names_upper])
   
    # Remove the matched country names from the 'Tags' column
    df['Tags'] = df.apply(lambda row: [tag for tag in row['Tags'] if tag not in row['Country_Topic']], axis=1)
    return df


def load_data(file_path):
    df = pd.read_csv(file_path)
    df = convert_columns_to_lists(df)
    #df = secure_categories(df, TOPICS_DICT, EDU_CATEGORIES, valid_languages, valid_sources) #ADDINg this line of code.
    df = transform_date_column(df)
    df = add_country_topic_column(df)
    return df

def get_categories(text, categories):
    """Finds categories in a given text."""
    found_categories = []
    
    # Ensure the input is a string; handle lists and arrays by joining their elements
    if isinstance(text, list) or isinstance(text, np.ndarray):
        text = ' '.join(map(str, text))  # Join elements into a single string
    elif not isinstance(text, str):
        text = str(text)  # Convert non-string types to string
    
    text = text.lower() # convert text to lower case

    for key in categories.keys():
        if any(word.lower() in text for word in categories[key]):
            found_categories.append(key.upper())

    return found_categories

def Validating_list_content(list_in_cell, valid_content_list):
    """
    Validates the content of a list (or a string) by comparing it to a list of valid elements.
    
    Args:
        list_in_cell (list or str): The list (or string) to validate.
        valid_content_list (list): The list of valid elements.
    
    Returns:
        list: A secured list containing only the valid elements.
    """
    # If input is a string, convert it into a list with one element
    if isinstance(list_in_cell, str):
        list_in_cell = [list_in_cell]
    
    # Validate elements
    secured_list = []
    for element in list_in_cell:
        if element in valid_content_list:
            secured_list.append(element)  # Keep the valid element
        else:
            print(f"Element '{element}' is not in the valid category. It was removed from the cell content.")
    
    return secured_list

def validate_source_string(source_string, valid_sources):
    """
    Validates a source string by comparing it to a list of valid sources.
    
    Args:
        source_string (str): The source string to validate.
        valid_sources (list): A list of valid source strings.
    
    Returns:
        str: The validated source string if valid, or an empty string if invalid.
    """
    if source_string in valid_sources:
        return source_string  # Return the valid source
    else:
        print(f"Source '{source_string}' is not in the valid category. It was removed.")
        return ""  # Return an empty string for invalid sources

def secure_categories(df, topics_dict, edu_categories, valid_languages, valid_sources):
    """
    Processes a DataFrame by applying specific transformations to selected columns.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        topics_dict (dict): Dictionary for finding categories in the 'Tags' column.
        edu_categories (dict): Dictionary for finding categories in the 'Type' column.
        valid_languages (list): List of valid languages for the 'Language' column.
        valid_sources (list): List of valid sources for the 'Source' column.
    
    Returns:
        pd.DataFrame: The processed DataFrame with updated columns.
    """
    # Process 'Tags' column with get_categories and TOPICS_DICT
    df['Tags'] = df['Tags'].apply(lambda x: get_categories(x, topics_dict))
    
    # Process 'Type' column with get_categories and EDU_CATEGORIES
    df['Type'] = df['Type'].apply(lambda x: get_categories(x, edu_categories))
    
    # Process 'Language' column with Validating_list_content and valid_languages
    df['Language'] = df['Language'].apply(lambda x: Validating_list_content(x, valid_languages))
    
    # Process 'Source' column with validate_source_string and valid_sources
    df['Source'] = df['Source'].apply(lambda x: validate_source_string(x, valid_sources))
    
    return df


def convert_columns_to_lists(df):
    # Convert columns with multiple values to lists
    df['Language'] = df['Language'].apply(lambda x: parse_cell(x) if pd.notnull(x) else [])
    df['Tags'] = df['Tags'].apply(lambda x: parse_cell(x) if pd.notnull(x) else [])
    df['Type'] = df['Type'].apply(lambda x: parse_cell(x) if pd.notnull(x) else [])
    return df


def transform_date_column(df):
    # Transform the 'Date' column
    df['Date'] = df['Date'].apply(lambda x: x.split('/')[1] if pd.notnull(x) and '/' in x else 'Undated')
    return df

# Function to add a title and subtitle
def set_title():
    # Set the font style

    title_html = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@300&display=swap');
            h1 {
                font-family: 'Oswald', sans-serif;
            }
        </style>
        <h1>               </h1>
    """
    st.markdown(title_html, unsafe_allow_html=True)

   
def sidebar_filters(df):
    st.sidebar.markdown("<h2 style='font-family: Oswald;'>FILTERS</h2>", unsafe_allow_html=True)

    # Extract individual values for each filter option
    individual_sources = list(df['Source'].unique())

    # Check for NaN values before exploding
    individual_languages = sorted(set(df['Language'].explode().dropna()))
    individual_tags = sorted(set(df['Tags'].explode().dropna()))
    individual_types = sorted(set(df['Type'].explode().dropna()))
    individual_years = sorted(set(df['Date'].unique()))

    # Create multiselects with individual values
    selected_language = st.sidebar.multiselect("Select Language", individual_languages)
    selected_tags = st.sidebar.multiselect("Select Tags", individual_tags)
    selected_types = st.sidebar.multiselect("Select Type", individual_types)
    selected_years = st.sidebar.multiselect("Select Year", individual_years)
    selected_source = st.sidebar.multiselect("Select Source", individual_sources)

    # Add keyword search
    keyword_search = st.sidebar.text_input("Keyword Search", "")

    # Add checkbox to filter out unavailable links
    filter_unavailable_links = st.sidebar.checkbox("Filter out unavailable links")

    return selected_source, selected_language, selected_tags, selected_types, selected_years, keyword_search, filter_unavailable_links

def apply_filters(df, selected_source, selected_language, selected_tags, selected_types, selected_years, keyword_search, filter_unavailable_links):
    # Apply filters to dataframe
    if selected_source:
        df = df[df['Source'].isin(selected_source)]
    if selected_language:
        df = df[df['Language'].apply(lambda x: any(lang in x for lang in selected_language))]
    if selected_tags:
        df = df[df['Tags'].apply(lambda x: any(tag in x for tag in selected_tags))]
    if selected_types:
        df = df[df['Type'].apply(lambda x: any(category in x for category in selected_types))]
    if selected_years:
        df = df[df['Date'].isin(selected_years)]
        
    # Apply filter to remove unavailable links
    if filter_unavailable_links:
        df = df[df['Link'] != "Link no longer available"]

    # Apply keyword search (case insensitive)
    if keyword_search:
        keyword_search = keyword_search.lower()
        df = df[df.apply(lambda row: any(keyword in str(row).lower() for keyword in keyword_search.split()), axis=1)]
   
    # Sort the filtered DataFrame by the 'Date' column (assuming it contains years) in descending order
    df['Date'] = pd.Categorical(df['Date'], categories=sorted(df['Date'].unique(), key=lambda x: (x != 'Undated', x)), ordered=True)
    df = df.sort_values(by='Date', key=lambda x: x == 'Undated', ascending=True).sort_values(by='Date', ascending=False)
   
    return df

   
def display_results(filtered_df):
    #st.subheader("Your search results")

    # List of columns to hide from the user
    columns_to_hide = ['PDF', 'HRE Produced?', 'Keyword Matches', 'Excerpt', 'RawText', 'Comments']

    # Rename the 'Country_Topic' column to 'Country Topic'
    filtered_df = filtered_df.rename(columns={'Country_Topic': 'Country Topic'})

    # Display the filtered data excluding the specified columns
    #st.write(filtered_df.drop(columns=columns_to_hide))
    # Display the filtered data excluding the specified columns
    st.markdown(
        f"""
        <style>
            .dataframe {{
                width: 100% !important;
                max-width: none !important;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.dataframe(filtered_df.drop(columns=columns_to_hide), height=600, width=1700)
   

# Dropdown Options
def get_sources():
    return valid_sources

def get_languages():
    return sorted(valid_languages)

def get_tags():
    # Filter out keys in TOPICS_DICT that also appear in COUNTRY_NAMES
    return sorted([key for key in TOPICS_DICT.keys() if key not in COUNTRY_NAMES])

def get_types():
    return sorted(EDU_CATEGORIES.keys())

# Function to validate input
def validate_form(link):
    if not link.strip():
        st.error("The Link is mandatory and cannot be empty.")
        return False
    return True

def flatten_and_uppercase(input_list):
    """
    Converts a list of strings into a single comma-separated string in uppercase.
    
    Args:
        input_list (list): List of strings.
    
    Returns:
        str: Comma-separated uppercase string or an empty string if input is None or empty.
    """
    return ", ".join([item.upper() for item in input_list]) if input_list else ""

# Function for "Submit a Resource" form
def form_page():
    st.title("Submit a Resource")

    # Create the form
    with st.form(key="submit_resource_form"):
        # User Inputs
        link = st.text_input("Link (Mandatory)", placeholder="Enter the output link here")
        title = st.text_input("Title (Optional)", placeholder="Enter the title here")
        source = st.selectbox("Source (Optional)", [""] + get_sources())
        language = st.multiselect("Language (Optional)", get_languages())  # Multiselect for Language
        tags = st.multiselect("Tags (Optional)", get_tags())  # Multiselect for Tags
        resource_type = st.multiselect("Type (Optional)", get_types())  # Multiselect for Type
        year = st.text_input("Year (Optional)", placeholder="Enter the year (e.g., 2024)")
    

        # Submit button inside the form
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Validate mandatory field
            if not link.strip():
                st.error("The Link field is mandatory. Please fill it out.")
                return
            # Process multiselect fields
            tags_str = flatten_and_uppercase(tags)
            type_str = flatten_and_uppercase(resource_type)
            language_str = flatten_and_uppercase(language)

            # Capture the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            # Prepare the data row
            f = lambda s: "NoInput" if len(s) == 0 else s
            row_data = [
                    f(source),       # Column 1: Source
                    f(title),        # Column 2: Title
                    link,         # Column 3: Link
                    f(language_str), # Column 4: Language
                    f(tags_str),     # Column 5: Tags
                    f(type_str),     # Column 6: Type
                    f(year),         # Column 7: Date
                    "NoInput",           # Column 8: Excerpt
                    "NoInput",           # Column 9: RawText
                    "NoInput",           # Column 10: Keyword Matches
                    "NoInput",           # Column 11: PDF
                    "NoInput",           # Column 12: HRE Produced?
                    "NoInput",           # Column 13: Comments
                    timestamp     # Column 14: Timestamp
                ]
                


            # Append the row to Google Sheets
            add_to_sheet(RESOURCE_SPREADSHEET_NAME, row_data)
            st.success("Your resource has been successfully submitted!")
            
def faq_page():
    st.title("Frequently Asked Questions")

    with st.expander("**What is the HRE Resource Hub?**"):
        st.write("""
        The HRE Resource Hub is a database containing over 6,000 human rights education (HRE) outputs created within the Amnesty International movement. This app allows users to search and filter a wide range of educational resources, including MOOCs, booklets, manuals, podcasts, videos—drawn from 70 national offices and spanning over 63 languages. 

The purpose of this database is to allow volunteers, staffers and members of the Amnesty International movement to access and leverage educational materials created by counterparts in other regions, preventing value loss, fostering collaboration, and enhancing knowledge exchange across borders.

""")

    with st.expander("**What kind of filters are available to refine my search?**"):
        st.write("""
        You can refine your search by language, type of resource (e.g., video, manual, etc), topic (‘indigenous rights’, ‘women’s rights’), date, and source. Additionally, you can use keyword search for particular expressions. We recommend broad terms for better results to ensure you don’t miss relevant outputs.
""")

    with st.expander("**What is included under the different ‘types’ of resources listed?**"):
        st.write("""
        - **MANUALS**: Thematic guides or workbooks for teachers, educators, and volunteers (e.g., “How to organize school debates,” “Facilitator’s guide,” or guides about a specific topic (e.g., “Basics of International Humanitarian Law”).
        - **ONLINE COURSES**: Academy courses created by the International Secretariat and other online courses created by Amnesty sections.  
        - **CLASSROOM ACTIVITIES**: Tools for interactive learning, such as quizzes, games, PowerPoint slides, puzzles, handouts, and session plans for in-class use.  
        - **VIDEOS**: Explanatory videos, animation videos, movies and documentaries recommended to teach human rights, announcements of film screening, audiovisual contests, recordings of online workshops.  
        - **MOVIES AND DOCUMENTARIES**: Any article that discusses or mentions movies or documentaries to teach human rights. This category is also included in the video category above.
        - **PODCASTS**: Podcasts or audio material.
        - **GET INVOLVED**: Participation forms for events and initiatives, workshop requests, newsletter subscriptions, and volunteer opportunities.
        - **ART AND HUMAN RIGHTS**: Initiatives that use posters, comics, artwork, photography exhibitions, and theater to teach human rights concepts.
        - **BOOK AND HUMAN RIGHTS**: Articles that discuss or mention books that can be used to teach human rights, including initiatives like school reading clubs for human rights, etc.
        - **ABOUT HRE**: Homepages and webpage sections dedicated to HRE (general information about the HRE program, news articles about HRE, announcements about HRE, HRE library in each website (if any).
        - **NEWS AND MORE**: News articles about HRE, announcements about HRE, HRE job openings, articles related to the human rights friendly school program, and others that dont fall under any of the above categories.
        - **BLOGS**: Blog posts (also included in the category ‘News and more’ above).
        """)

    with st.expander("**Can I combine filters? (For example, ‘children’ and ‘videos’)**"):
        st.write("""
        Yes, you can use multiple filters to further refine your search.
        """)

    with st.expander("**Where is the data in this database sourced from?**"):
        st.write("""
        Our sources include:  
        - Official websites from the International Secretariat and national sections.  
        - YouTube channels from the International Secretariat and national sections.  
        - Additional websites that contain online courses or materials.
        """)

    with st.expander("**How often is the database updated?**"):
        st.write("""
        This database will be updated on a yearly basis, but you can submit resources for inclusion in the database at any time.
        """)

    with st.expander("**How are broken links handled?**"):
        st.write("""
        Some outputs in the database, such as temporary resources or announcements of past events, may contain links that are no longer available at the time of your search.
We will conduct periodic reviews to identify and address broken links. When replacement links are unavailable, these outputs will be labeled as unavailable. To exclude outputs with broken links, use the checkbox filter located at the end of the sidebar filters.
As a policy, outputs with broken links or unavailable resources will not be deleted. Instead, they will be retained for monitoring and evaluation purposes.
""")

    with st.expander("**Can I download the full database?**"):
        st.write("""
        Yes, you can download the full database or a filtered subset by clicking the download icon at the top-right corner. The file will be saved as a CSV, which can be opened in Excel, Google Sheets, or other database management tools.
""")

    with st.expander("**How can I submit a new resource to the database?**"):
        st.write("""
        If you know of HRE outputs that are not included in the database, you can submit them by clicking **Submit a resource** under the Navigation menu at the top-left corner. Newly submitted resources may not appear immediately as submissions are reviewed and pre-approved by the HRE team before being uploaded to the general database.
""")

    with st.expander("**How can I report errors or suggest improvements to this database?**"):
        st.write("""
        If you notice errors, such as an incorrect label (e.g., wrong language or type), please report them by clicking **Report error** under the **Navigation** menu at the top-left corner. Alternatively, you can email us at *****email address.
We also welcome suggestions for improving the database through this channel.

        """)

    with st.expander("**What is the criteria used for selecting outputs that are included in the database?**"):
        st.write("""
        - Output has the expression “academy”, “human rights education”, “human rights friendly school” or similar.
        - Output offers, or re-directs to a self-paced online course.
        - Output offers pedagogical resources for teaching specific human rights topics.
        - Output offers audiovisual resources that can be used for educational purposes, such as documentaries and animated videos.
        - Output announces or discusses any of the latter.
 """)

def report_issue_page():
    st.title("Report an Issue")
    
    st.markdown("""
    If you noticed an error, such as an incorrect label (e.g., wrong language or type), please tell us so that we can fix it!
      
    We also welcome suggestions for improving the HRE Resource Hub.  
    """)
    
    # Create form for reporting issues
    with st.form(key="report_issue_form"):
        issue_description = st.text_area("Describe the issue*", placeholder="Describe the issue or suggestion here...")
        contact_info = st.text_input("Contact Information (Optional)", placeholder="Email address or other contact info")
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            if not issue_description.strip():
                st.warning("Please describe the issue before submitting.")
                return
            # Capture the current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            # Prepare the row data
            row_data = [issue_description, contact_info, timestamp]  # Issue, Contact, Timestamp

            # Append the row to the Google Sheets
            add_to_sheet(ISSUE_SPREADSHEET_NAME, row_data)
            st.success("Thank you for your feedback!")

    st.markdown("""
    You could also email us at **email address**.
    """)


            
def main(file_path):
    st.set_page_config(layout="wide", page_title="HRE Resource Hub")
    
    # Navigation in Sidebar
    st.sidebar.title("NAVIGATION")
    app_mode = st.sidebar.selectbox("Select", [
        "See all resources", 
        "Submit a resource", 
        "Frequently asked questions", 
        "Report an issue"
    ])
    
    if app_mode == "See all resources":
        main_page(file_path)
    elif app_mode == "Submit a resource":
        form_page()
    elif app_mode == "Frequently asked questions":
        faq_page()
    elif app_mode == "Report an issue":
        report_issue_page()

def main_page(file_path):
    set_title()
    set_bg_hack('background_image12.png')
    col1, col2 = st.columns([1, 9])
    df = load_data(file_path)
    selected_source, selected_language, selected_tags, selected_types, selected_years, keyword_search, filter_unavailable_links = sidebar_filters(df)
    filtered_df = apply_filters(df, selected_source, selected_language, selected_tags, selected_types, selected_years, keyword_search, filter_unavailable_links)
    display_results(filtered_df)
    youtube_video_url = "https://www.youtube.com/watch?v=_TpQubxoH50"
    st.sidebar.markdown("<h3 style='font-family: Oswald;'>TUTORIAL: HOW TO USE THIS DATABASE</h3>", unsafe_allow_html=True)
    st.sidebar.video(youtube_video_url)
 
   
if __name__ == "__main__":
    # Specify the local file path to your CSV file
    local_file_path = 'latest_dataset11.csv'
    main(local_file_path) 
    
    
