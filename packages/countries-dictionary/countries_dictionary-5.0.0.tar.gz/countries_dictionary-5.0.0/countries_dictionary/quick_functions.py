from countries_dictionary import COUNTRIES
from countries_dictionary.russia import RUSSIA
from countries_dictionary.united_states import UNITED_STATES
from countries_dictionary.vietnam import VIETNAM
import json

def quick_function(action: str, dictionary="countries"):
    """Returns one of the dictionaries depends on the `dictionary` parameter and modify it depends on the `action` parameter."""
    match dictionary.casefold():
        case "countries": x = COUNTRIES
        case "russia": x = RUSSIA
        case "united states" | "america": x = UNITED_STATES
        case "vietnam": x = VIETNAM
        case _: raise Exception("This dictionary does not exist (yet)")
    if action == (): raise Exception("No action was provided")
    match action.casefold():
        case "population density":
            for y in x:
                if x == COUNTRIES: x[y]["population density"] = COUNTRIES[y]["population"] / COUNTRIES[y]["land area"]
                else: x[y]["population density"] = x[y]["population"] / x[y]["area"]
        case "GDP per capita":
            if x != COUNTRIES:
                for y in x: x[y]["GDP per capita"] = COUNTRIES[y]["nominal GDP"] / COUNTRIES[y]["population"]
            else: raise Exception("Only works with the Countries Dictionary")
        case "ISO 3166-2":
            if x == COUNTRIES:
                for y in x: x[y]["ISO 3166-2"] = "ISO 3166-2:" + COUNTRIES[y]["ISO 3166-1"]["alpha-2"]
            else: raise Exception("Only works with the Countries Dictionary")
    return x

def json_dictionary(action: str, indent: int | str | None = None, dictionary="countries"):
    """Converts a dictionary into a JSON string"""
    x = quick_function(action, dictionary)
    return json.dumps(x, indent=indent)

def json_dictionary(action: str, chosen_key: str, reverse: bool = True, dictionary="countries"):
    """Sorts a dictionary by a sortable key"""
    x = quick_function(action, dictionary)
    return dict(sorted(x.items(), key=lambda item: item[1][chosen_key], reverse=reverse))

#def filtered_dictionary(chosen_key: str, chosen_value: int | str, dictionary="countries"):
#    """Filters the chosen dictionary by a key"""
#    x = chosen_dictionary(dictionary)
#    if chosen_key == "continents" or chosen_key == "official languages":
#        return dict(filter(lambda item: chosen_value in item[1][chosen_key], x.items()))
#    else: return dict(filter(lambda item: item[1][chosen_key] == chosen_value, x.items()))
# This is still under development

# Fun functions, for entertainment purposes only (moving to quick_function()!)

#def countries_france_censored():
#    """Returns the countries dictionary with the `France` key gets censored `Fr*nce`
#
#    (This is just a joke, I don't support hate against France and French people)"""
#    new_countries = COUNTRIES
#    new_countries["Fr*nce"] = new_countries.pop("France")
#    new_countries = dict(sorted(new_countries.items()))
#    return new_countries

#def countries_allahu_akbar():
#    """Returns the countries dictionary without most countries except the two countries whose mottos are "God is the Greatest". اَللَّٰهُ أَكْبَرُ!
#
#    (I'm not a Muslim, and this is just a joke, I don't support hate against Islam and these two countries)"""
#    return dict(filter(lambda item: item[1]["motto"] == "God is the Greatest", COUNTRIES.items()))
