import googlemaps

def get_place_details(place_ids, api_key):
    """
    Obtém detalhes dos lugares especificados pelo place_ids.
    place_ids: Lista de string - lista de place_ids para buscar detalhes
    Retorna uma lista de dicionários com os detalhes dos lugares.
    """
    gmaps = googlemaps.Client(key=api_key)
    place_details = []
    
    for place_id in place_ids:
        result = gmaps.place(place_id)
        place_details.append(result)
    return place_details