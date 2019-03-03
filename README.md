# kalliope_neuron_osrm

## Synopsis
Neuron to use the [OpenSourceRoutingMachine](http://project-osrm.org/) API to

* get route from coordinates
* get summary for this route
* get distance for this route
* get estimated duration for this route

## Installation
```
kalliope install --git-url https://github.com/redSpoutnik/kalliope_neuron_osrm.git
```

# Options

| parameter    | required | default                 | choices   | comment |
|--------------|----------|-------------------------|-----------|---------|
| host         | NO       | router.project-osrm.org | string    |         |
| profile      | NO       | driving                 | string    | Mode of transportation, see [OSRM doc](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#requests). |
| latitude1    | YES      | None                    | float     | float or string representing a float |
| longitude1   | YES      | None                    | float     | float or string representing a float |
| latitude2    | YES      | None                    | float     | float or string representing a float |
| longitude2   | YES      | None                    | float     | float or string representing a float |
| alternatives | NO       | False                   | bool, int | Set a limit to the number of routes to return. Must be positive integer or boolean value, see [OSRM doc](https://github.com/Project-OSRM/osrm-backend/blob/master/docs/http.md#route-service). |
| distance     | NO       | None                    | bool      | Append distance data in output. |
| duration     | NO       | None                    | bool      | Append duration data in output. |
| summary      | NO       | None                    | bool      | Append summary data in output. |
| route        | NO       | None                    | bool      | Append route data in output. |
| raw          | NO       | None                    | bool      | Append raw data in output. |

* From among at least one of **"distance"**, **"duration"**, **"summary"**, **"route"** or **"raw"** must be set to **True**

## Return Values

| Name       | Description                                     | Type   |
|------------|-------------------------------------------------|--------|
| returncode | "OK" if host can be reached, error code however | string |
| start      | Start coordinates representation                | string |
| end        | End coordinates representation                  | string |
| profile    | Profile used to calcul routes                   | string |
| raw        | Raw json from API response, may be present only if **"raw"** parameter was set to True | dict   |
| routes     | Routes data list                                | list   |

### Routes Data Structure

* **routes** (list of dicts) containing :
    * **distance** (dict) containing :
        * **kilometers** (int) distance in kilometers
        * **meters** (int) remaining meters
    * **duration** (dict) containing :
        * **days** (int) duration in days
        * **hours** (int) remaining hours
        * **minutes** (int) remaining minutes
        * **seconds** (int) remaining seconds
    * **summary** (string) principal roads
    * **route** (dict) containing :
        * **number_steps** (int) steps length
        * **steps** (list of dicts) containing :
            * **name** (string) road or street name
            * **maneuver** (string) maneuver type
            * **direction** (string) maneuver direction, if any

**distance**, **duration**, **summary** and **route** are present only if correspounding options have been set to **True**

## Synapses example

Get route between Paris and Grenoble
```yaml
  - name: "osrm-paris-grenoble"
    signals:
      - order: "get route from Paris to Grenoble"
    neurons:
      - routing_machine:
          latitude1: 48.8566101
          longitude1: 2.3514992
          latitude2: 45.1875602
          longitude2: 5.7357819
          distance: True
          duration: True
          summary: True
          route: True
          file_template: "templates/osrm_search.j2"
```

Using [Nominatim neuron](https://github.com/redSpoutnik/kalliope_neuron_nominatim) for geocoding and passing coordinates by [kalliope memory](https://kalliope-project.github.io/kalliope/brain/brain/)
```yaml
  - name: "osrm-paris"
    signals:
      - order: "get route from Paris to {{ address }}"
    neurons:
      - nominatim:
          language: "fr"
          operation: "geocode"
          address: "{{ address }}"
          kalliope_memory:
            osrm-home-latitude: "{{ latitude }}"
            osrm-home-longitude: "{{ longitude }}"
      - routing_machine:
          latitude1: 48.8566101
          longitude1: 2.3514992
          latitude2: "{{ kalliope_memory['osrm-paris-latitude'] }}"
          longitude2: "{{ kalliope_memory['osrm-paris-longitude'] }}"
          distance: True
          duration: True
          summary: True
          route: True
          file_template: "templates/osrm_search.j2"
```

```yaml
  - name: "osrm-route"
    signals:
      - order: "get route from {{ address1 }} to {{ address2 }}"
    neurons:
      - nominatim:
          language: "fr"
          operation: "geocode"
          address: "{{ address1 }}"
          kalliope_memory:
            osrm-route-start-latitude: "{{ latitude }}"
            osrm-route-start-longitude: "{{ longitude }}"
      - nominatim:
          language: "fr"
          operation: "geocode"
          address: "{{ address2 }}"
          kalliope_memory:
            osrm-route-end-latitude: "{{ latitude }}"
            osrm-route-end-longitude: "{{ longitude }}"
      - routing_machine:
          latitude1: "{{ kalliope_memory['osrm-route-start-latitude'] }}"
          longitude1: "{{ kalliope_memory['osrm-route-start-longitude'] }}"
          latitude2: "{{ kalliope_memory['osrm-route-end-latitude'] }}"
          longitude2: "{{ kalliope_memory['osrm-route-end-longitude'] }}"
          distance: True
          duration: True
          summary: True
          route: True
          file_template: "templates/osrm_search.j2"
```

Following template for ```osrm_search.j2``` should handle every usages
```
{% if returncode == "OK" %}
  {% for route in routes %}
    {% if route['distance'] is defined %}
      route distance is {% if route['distance']['kilometers'] > 0 %} {{ route['distance']['kilometers'] }} kilometers and {% endif %} {{ route['distance']['meters'] }} meters
    {% endif %}
    {% if route['duration'] is defined %}
      route duration is estimated at {% if route['duration']['days'] > 0 %} {{ route['duration']['days'] }} days, {% endif %} {% if route['duration']['hours'] > 0 %} {{ route['duration']['hours'] }} hours and {% endif %} {% if route['duration']['minutes'] > 0 %} {{ route['duration']['minutes'] }} minutes {% endif %}
    {% endif %}
    {% if route['summary'] is defined %}
      the route transit through {{ route['summary'] }}
    {% endif %}
    {% if route['steps'] is defined %}
        There are {{ route['number_steps'] }} steps
        {% for step in route['steps'] %}
          {{
            step['maneuver']
          }} {% if step['direction'] is not none %} {{
            step['direction']
          }} {% endif %}, {{ 
            step['name'] 
          }}
        {% endfor %}
    {% endif %}
  {% endfor %}
{% else %}
    the server is not available
{% endif %}
```
