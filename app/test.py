import watson_developer_cloud
import pprint
import requests
import json

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

pp = pprint.PrettyPrinter(indent=4)
#put you API key here
mapsApiKey = 'api_key'

conversation = watson_developer_cloud.ConversationV1(
  #Watson Conversation username and password here
  username = 'username',
  password = 'password',
  version = '2017-05-26'
)
#Your Waston Conversation Workspace ID
workspace_id = 'workspace ID'

user_input = ''
context = {}
intent = []

def recipeSearch(query):
    labels = []
    #Add your Edamam APPID and APPKEY below
    result = requests.get("https://api.edamam.com/search?q="+query+"&app_id=APPID&app_key=APPKEY")
    data = result.json()

    for recipe in data['hits']:
        if recipe.get('recipe') and recipe['recipe'].get('label') and recipe['recipe'].get('shareAs'):
            labels.append({'name': recipe['recipe']['label'], 'share':recipe['recipe']['shareAs']})
    return len(labels), labels

def mapsSearch(city, cuisine):
    query = cuisine + ',' + city
    restaurants = []
    #Replace KEY with your Google Maps API key
    result = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json?query='+query+'&key=KEY')
    result = result.json()
    if len(result['results']):
        for place in result['results']:
            restaurants.append({'name':place['name'],'address':place['formatted_address']})
    return len(result['results']), restaurants

def chat(context, user_input, intent):
    r = ''
    response = conversation.message(
      workspace_id = workspace_id,
      input = {
        'text': user_input,
      },
      context = context
    )

    # pp.pprint(response)
    context = response['context']

    # if len(response['entities']):
    #     print response['entities'][0]['value']
    #
    # if response['intents']:
    #   print('Detected intent: #' + response['intents'][0]['intent'])

    if response['intents'] != []:
        intent = response['intents']
    # print intent

    if len(intent) and intent[0]['intent'] == 'stayingin' and response['context'].get('food') and response['context'].get('allergies') and not is_number(user_input):
        numberOfRecipes, labels = recipeSearch(response['context']['food']+','+response['context']['allergies'])
        if len(labels) > 0:
            context['numberOfRecipes'] = numberOfRecipes
            context['recipes'] = labels
        else:
            context['numberOfRecipes'] = 0
        response = conversation.message(
          workspace_id = workspace_id,
          input = {
            'text': user_input,
          },
          context = context
        )
        if response['output']['text']:
          # print(response['output']['text'][0])
          r += response['output']['text'][0] + ' '
        for x in range(0,len(labels)):
            # print '(' + str(x + 1) + ') ' + labels[x]['name']
            r += '(' + str(x + 1) + ') ' + labels[x]['name'] + ' '

    if response['context'].get('recipes') and is_number(user_input) and int(user_input) > 0 and int(user_input) <= len(response['context']['recipes']):
        r += 'Good choice, here is a link to the recipe ' + response['context']['recipes'][int(user_input) - 1]['share']
        response['context'].pop('recipes')
        response['context'].pop('numberOfRecipes')
        response['context'].pop('food')
        response['context'].pop('allergies')
    else:
        if response['context'].get('recipes') and is_number(user_input) and (int(user_input) <= 0 or int(user_input) > len(response['context']['recipes'])):
            r += 'Please enter a number between 1 and ' + str(len(response['context']['recipes']))

    if len(intent) and intent[0]['intent'] == 'eatingout' and response['context'].get('location') and response['context'].get('cuisine') and not is_number(user_input):
        numberOfPlaces, restaurants = mapsSearch(response['context']['location'], response['context']['cuisine'])
        if numberOfPlaces > 0:
            context['places'] = numberOfPlaces
            context['restaurants'] = restaurants
        else:
            context['places'] = 0
        response = conversation.message(
          workspace_id = workspace_id,
          input = {
            'text': user_input,
          },
          context = context
        )
        if response['output']['text']:
          # print(response['output']['text'][0])
          r += response['output']['text'][0] + ' '
        for x in range(0,len(restaurants)):
            r += '(' + str(x + 1) + ') ' + restaurants[x]['name'] + ' '
        # print 'r = ', r

    if response['context'].get('restaurants') and is_number(user_input) and int(user_input) > 0 and int(user_input) <= len(response['context']['restaurants']):
        r += 'Alright, let\'s go to ' + response['context']['restaurants'][int(user_input) - 1]['name'] + ' '
        r += 'The address is: ' + response['context']['restaurants'][int(user_input) - 1]['address'] + ' '
        response['context'].pop('restaurants')
        response['context'].pop('cuisine')
        response['context'].pop('location')
        response['context'].pop('places')
    else:
        if response['context'].get('restaurants') and is_number(user_input) and (int(user_input) <= 0 or int(user_input) > len(response['context']['restaurants'])):
            r += 'Please enter a number between 1 and ' + str(len(response['context']['restaurants']))
    if r == '' and response['output']['text']:
      r = response['output']['text'][0]

    return response['context'], intent, response['output'], r

if __name__ == "__main__":
    user_input = ''
    intent = []
    context = {}
    while True:
        context, intent, output, response = chat(context, user_input, intent)
        print response
        if output.get('action') and output['action'] == 'end_conversation':
            break
        user_input = raw_input('>> ')
