from mcp.server.fastmcp import FastMCP
import requests
from typing import Dict, Optional, List
from location_config import ArcGISApiKeyManager

# Create an MCP server
mcp = FastMCP(name="Location MCP Demo", 
              description="A MCP demo server for location-based services",
              version="0.1.0",
              port=8000)


def geocode_address(address: str, api_key: Optional[str] = None) -> Dict:
    """
    Geocode an address using ArcGIS Location Platform Geocoding Services
    
    Args:
        address: The address string to geocode
        api_key: Optional API key for ArcGIS services (uses free service if not provided)
    
    Returns:
        Dictionary containing geocoded result with coordinates and metadata
    """
    # ArcGIS World Geocoding Service endpoint
    base_url = "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
    
    params = {
        "singleLine": address,
        "f": "json",
        "outFields": "Addr_type,Type,PlaceName,Place_addr,Phone,URL,Rank",
        "maxLocations": 1
    }
    
    # Add API key to parameters if provided
    ArcGISApiKeyManager.add_key_to_params(params, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("candidates") and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            
            return {
                "success": True,
                "address": address,
                "formatted_address": candidate.get("address", ""),
                "coordinates": {
                    "latitude": candidate["location"]["y"],
                    "longitude": candidate["location"]["x"]
                },
                "score": candidate.get("score", 0),
                "attributes": candidate.get("attributes", {}),
                "raw_response": candidate
            }
        else:
            return {
                "success": False,
                "address": address,
                "error": "No geocoding results found",
                "coordinates": None
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "address": address,
            "error": f"Geocoding request failed: {str(e)}",
            "coordinates": None
        }
    except Exception as e:
        return {
            "success": False,
            "address": address,
            "error": f"Geocoding error: {str(e)}",
            "coordinates": None
        }

def search_nearby_places(latitude: float, longitude: float, category: Optional[str] = None, radius: int = 1000, max_results: int = 10, api_key: Optional[str] = None) -> Dict:
    """
    Search for nearby places using ArcGIS Location Platform Places Services
    
    Args:
        latitude: The latitude coordinate to search around
        longitude: The longitude coordinate to search around
        category: Optional category filter (e.g., 'restaurant', 'gas_station', 'park')
        radius: Search radius in meters (default: 1000m)
        max_results: Maximum number of results to return (default: 10)
        api_key: Optional API key for ArcGIS services
    
    Returns:
        Dictionary containing nearby places with their details and coordinates
    """
    # ArcGIS Places API endpoint for nearby search
    base_url = "https://places-api.arcgis.com/arcgis/rest/services/places-service/v1/places/near-point"
    
    params = {
        "x": longitude,
        "y": latitude,
        "radius": radius,
        "maxResults": max_results,
        "f": "json"
    }
    
    # Add category filter if provided
    if category:
        params["categoryIds"] = category
    
    # Add API key to parameters if provided
    ArcGISApiKeyManager.add_key_to_params(params, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("results") and len(data["results"]) > 0:
            places = []
            for place in data["results"]:
                place_info = {
                    "name": place.get("name", "Unknown"),
                    "place_id": place.get("placeId", ""),
                    "categories": place.get("categories", []),
                    "address": place.get("address", {}).get("label", ""),
                    "coordinates": {
                        "latitude": place.get("location", {}).get("y", 0),
                        "longitude": place.get("location", {}).get("x", 0)
                    },
                    "distance": place.get("distance", 0),
                    "phone": place.get("contactInfo", {}).get("telephone", ""),
                    "website": place.get("contactInfo", {}).get("website", ""),
                    "rating": place.get("rating", 0),
                    "price_level": place.get("price", ""),
                    "hours": place.get("hours", {}),
                    "raw_data": place
                }
                places.append(place_info)
            
            return {
                "success": True,
                "search_location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "category_filter": category,
                "radius_meters": radius,
                "total_results": len(places),
                "places": places,
                "raw_response": data
            }
        else:
            return {
                "success": True,
                "search_location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "category_filter": category,
                "radius_meters": radius,
                "total_results": 0,
                "places": [],
                "message": "No places found in the specified area"
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "search_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "category_filter": category,
            "radius_meters": radius,
            "total_results": 0,
            "error": f"Places search request failed: {str(e)}",
            "places": []
        }
    except Exception as e:
        return {
            "success": False,
            "search_location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "category_filter": category,
            "radius_meters": radius,
            "total_results": 0,
            "error": f"Places search error: {str(e)}",
            "places": []
        }

def reverse_geocode_coordinates(latitude: float, longitude: float, api_key: Optional[str] = None) -> Dict:
    """
    Reverse geocode coordinates using ArcGIS Location Platform Reverse Geocoding Services
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        api_key: Optional API key for ArcGIS services (uses free service if not provided)
    
    Returns:
        Dictionary containing reverse geocoded result with address and metadata
    """
    # ArcGIS World Geocoding Service reverse geocoding endpoint
    base_url = "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode"
    
    params = {
        "location": f"{longitude},{latitude}",  # ArcGIS expects x,y (lon,lat) format
        "f": "json",
        "outSR": "4326",  # WGS84 spatial reference
        "returnIntersection": "false"
    }
    
    # Add API key to parameters if provided
    ArcGISApiKeyManager.add_key_to_params(params, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("address"):
            address_info = data["address"]
            
            return {
                "success": True,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "formatted_address": address_info.get("Match_addr", ""),
                "address_components": {
                    "street": address_info.get("Address", ""),
                    "city": address_info.get("City", ""),
                    "state": address_info.get("Region", ""),
                    "postal_code": address_info.get("Postal", ""),
                    "country": address_info.get("CountryCode", "")
                },
                "location_type": data.get("location", {}).get("spatialReference", {}).get("wkid", ""),
                "raw_response": data
            }
        else:
            return {
                "success": False,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "error": "No reverse geocoding results found",
                "formatted_address": None
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "error": f"Reverse geocoding request failed: {str(e)}",
            "formatted_address": None
        }
    except Exception as e:
        return {
            "success": False,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "error": f"Reverse geocoding error: {str(e)}",
            "formatted_address": None
        }


def get_elevation(latitude: float, longitude: float, api_key: Optional[str] = None) -> Dict:
    """
    Get elevation data for coordinates using ArcGIS Location Platform Elevation Services
    
    Args:
        latitude: The latitude coordinate
        longitude: The longitude coordinate
        api_key: Optional API key for ArcGIS services (uses free service if not provided)
    
    Returns:
        Dictionary containing elevation result with metadata
    """
    # ArcGIS Location Platform Elevation Service endpoint
    base_url = "https://elevation-api.arcgis.com/arcgis/rest/services/WorldElevation/Terrain/ImageServer/identify"
    
    params = {
        "f": "json",
        "geometry": f"{longitude},{latitude}",
        "geometryType": "esriGeometryPoint",
        "returnGeometry": "false",
        "returnCatalogItems": "false"
    }
    
    # Add API key to parameters if provided
    ArcGISApiKeyManager.add_key_to_params(params, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("value") is not None:
            # Extract elevation data from response
            elevation_meters = data["value"]
            elevation_feet = elevation_meters * 3.28084  # Convert meters to feet
            
            return {
                "success": True,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "elevation": {
                    "meters": elevation_meters,
                    "feet": round(elevation_feet, 2)
                },
                "data_source": "ArcGIS Location Platform Elevation Service",
                "raw_response": data
            }
        else:
            return {
                "success": False,
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "error": "No elevation data available for these coordinates",
                "elevation": None
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "error": f"Network error: {str(e)}",
            "elevation": None
        }
    except Exception as e:
        return {
            "success": False,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "error": f"Error getting elevation: {str(e)}",
            "elevation": None
        }


def get_directions_between_locations(origin: str, destination: str, travel_mode: str = "driving", api_key: Optional[str] = None) -> Dict:
    """
    Get directions and routing information between two locations using ArcGIS Location Platform Routing Services
    
    Args:
        origin: The starting location (address or coordinates as "lat,lon")
        destination: The ending location (address or coordinates as "lat,lon") 
        travel_mode: Transportation mode - "driving", "walking", or "trucking" (default: "driving")
        api_key: Optional API key for ArcGIS services (uses free service if not provided)
    
    Returns:
        Dictionary containing routing result with directions, travel time, and distance
    """
    # ArcGIS World Route Service endpoint
    base_url = "https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
    
    # Convert travel mode to ArcGIS impedance attribute
    travel_mode_mapping = {
        "driving": "Drive Time",
        "walking": "Walk Time", 
        "trucking": "Truck Travel Time"
    }
    
    impedance = travel_mode_mapping.get(travel_mode.lower(), "Drive Time")
    
    # Geocode addresses if they are not coordinates
    try:
        # Check if origin is coordinates (lat,lon format) or address
        if "," in origin and len(origin.split(",")) == 2:
            try:
                lat, lon = [float(x.strip()) for x in origin.split(",")]
                origin_coords = f"{lon},{lat}"  # ArcGIS expects x,y (lon,lat)
            except ValueError:
                # If parsing fails, treat as address and geocode
                geocode_result = geocode_address(origin, api_key)
                if not geocode_result["success"]:
                    return {
                        "success": False,
                        "origin": origin,
                        "destination": destination,
                        "travel_mode": travel_mode,
                        "error": f"Failed to geocode origin: {geocode_result['error']}"
                    }
                coords = geocode_result["coordinates"]
                origin_coords = f"{coords['longitude']},{coords['latitude']}"
        else:
            # Geocode address
            geocode_result = geocode_address(origin, api_key)
            if not geocode_result["success"]:
                return {
                    "success": False,
                    "origin": origin,
                    "destination": destination,
                    "travel_mode": travel_mode,
                    "error": f"Failed to geocode origin: {geocode_result['error']}"
                }
            coords = geocode_result["coordinates"]
            origin_coords = f"{coords['longitude']},{coords['latitude']}"
        
        # Check if destination is coordinates (lat,lon format) or address  
        if "," in destination and len(destination.split(",")) == 2:
            try:
                lat, lon = [float(x.strip()) for x in destination.split(",")]
                dest_coords = f"{lon},{lat}"  # ArcGIS expects x,y (lon,lat)
            except ValueError:
                # If parsing fails, treat as address and geocode
                geocode_result = geocode_address(destination, api_key)
                if not geocode_result["success"]:
                    return {
                        "success": False,
                        "origin": origin,
                        "destination": destination,
                        "travel_mode": travel_mode,
                        "error": f"Failed to geocode destination: {geocode_result['error']}"
                    }
                coords = geocode_result["coordinates"]
                dest_coords = f"{coords['longitude']},{coords['latitude']}"
        else:
            # Geocode address
            geocode_result = geocode_address(destination, api_key)
            if not geocode_result["success"]:
                return {
                    "success": False,
                    "origin": origin,
                    "destination": destination,
                    "travel_mode": travel_mode,
                    "error": f"Failed to geocode destination: {geocode_result['error']}"
                }
            coords = geocode_result["coordinates"]
            dest_coords = f"{coords['longitude']},{coords['latitude']}"
            
    except Exception as e:
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode,
            "error": f"Error processing locations: {str(e)}"
        }
    
    # Prepare routing parameters
    stops = f"{origin_coords};{dest_coords}"
    
    params = {
        "stops": stops,
        "f": "json",
        "returnDirections": "true",
        "returnRoutes": "true", 
        "returnStops": "true",
        "impedanceAttributeName": impedance,
        "directionsOutputType": "complete",
        "directionsStyleName": "NA Desktop",
        "directionsLengthUnits": "miles",
        "directionsTimeAttributeName": impedance,
        "outputGeometryPrecision": 3,
        "outputGeometryPrecisionUnits": "decimalDegrees"
    }
    
    # Add API key to parameters if provided
    ArcGISApiKeyManager.add_key_to_params(params, api_key)
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for routing errors
        if data.get("error"):
            return {
                "success": False,
                "origin": origin,
                "destination": destination,
                "travel_mode": travel_mode,
                "error": f"Routing error: {data['error'].get('message', 'Unknown routing error')}"
            }
        
        # Extract route information
        routes = data.get("routes", {}).get("features", [])
        directions_info = data.get("directions", [])
        
        if not routes:
            return {
                "success": False,
                "origin": origin,
                "destination": destination,
                "travel_mode": travel_mode,
                "error": "No route found between the specified locations"
            }
        
        route = routes[0]  # Get first (and typically only) route
        attributes = route.get("attributes", {})
        
        # Extract step-by-step directions
        directions = []
        if directions_info:
            directions_features = directions_info[0].get("features", [])
            for step in directions_features:
                step_attrs = step.get("attributes", {})
                directions.append({
                    "instruction": step_attrs.get("text", ""),
                    "distance": step_attrs.get("length", 0),
                    "time": step_attrs.get("time", 0),
                    "maneuver_type": step_attrs.get("maneuverType", "")
                })
        
        # Calculate total time and distance
        total_time_minutes = attributes.get("Total_" + impedance.replace(" ", "_"), 0)
        total_distance_miles = attributes.get("Total_Miles", 0)
        
        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode,
            "route_summary": {
                "total_time_minutes": round(total_time_minutes, 1),
                "total_distance_miles": round(total_distance_miles, 2),
                "total_time_formatted": f"{int(total_time_minutes // 60)}h {int(total_time_minutes % 60)}m" if total_time_minutes >= 60 else f"{int(total_time_minutes)}m"
            },
            "directions": directions,
            "route_geometry": route.get("geometry", {}),
            "raw_response": data
        }
        
    except requests.RequestException as e:
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "travel_mode": travel_mode,
            "error": f"Routing request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "origin": origin,
            "destination": destination, 
            "travel_mode": travel_mode,
            "error": f"Routing error: {str(e)}"
        }

def format_directions_for_chat(routing_result: Dict) -> str:
    """
    Format routing results for display in chat UI
    
    Args:
        routing_result: Result from get_directions_between_locations
        
    Returns:
        Formatted markdown string for chat display
    """
    if not routing_result.get("success"):
        return f"❌ **Routing Failed**\n\nError: {routing_result.get('error', 'Unknown error')}"
    
    summary = routing_result["route_summary"]
    directions = routing_result.get("directions", [])
    travel_mode = routing_result.get("travel_mode", "driving").capitalize()
    
    # Build the formatted response
    response = f"🗺️ **{travel_mode} Directions**\n\n"
    response += f"📍 **From:** {routing_result['origin']}\n"
    response += f"🎯 **To:** {routing_result['destination']}\n\n"
    response += f"⏱️ **Travel Time:** {summary['total_time_formatted']}\n"
    response += f"📏 **Distance:** {summary['total_distance_miles']} miles\n\n"
    
    if directions:
        response += "📋 **Turn-by-Turn Directions:**\n"
        for i, step in enumerate(directions[:10], 1):  # Limit to first 10 steps for readability
            instruction = step.get("instruction", "").strip()
            if instruction:
                distance = step.get("distance", 0)
                if distance > 0:
                    response += f"{i}. {instruction} ({distance:.1f} miles)\n"
                else:
                    response += f"{i}. {instruction}\n"
        
        if len(directions) > 10:
            response += f"... and {len(directions) - 10} more steps\n"
    
    return response


@mcp.tool()
def geocode(address: str) -> Dict:
    """
    Geocode an address and return coordinates with metadata
    
    Args:
        address: The address string to geocode
        
    Returns:
        Geocoded result with coordinates and metadata
    """
    return geocode_address(address)

@mcp.tool()
def find_places(location: str, category: Optional[str] = None, radius: int = 1000, max_results: int = 10) -> Dict:
    """
    Find nearby places around a given location with optional category filtering
    
    Args:
        location: Address or location description to search around
        category: Optional category filter (e.g., 'restaurant', 'gas_station', 'park', 'hotel', 'hospital')
        radius: Search radius in meters (default: 1000m, max: 50000m)
        max_results: Maximum number of results to return (default: 10, max: 50)
        
    Returns:
        Dictionary containing nearby places with details and map visualization options
    """
    # Validate inputs
    radius = min(max(radius, 10), 50000)  # Clamp between 10m and 50km
    max_results = min(max(max_results, 1), 50)  # Clamp between 1 and 50
    
    # First geocode the location
    geocode_result = geocode_address(location)
    if not geocode_result["success"]:
        return {
            "success": False,
            "error": f"Failed to geocode location '{location}': {geocode_result['error']}"
        }
    
    coords = geocode_result["coordinates"]
    latitude = coords["latitude"]
    longitude = coords["longitude"]
    
    # Search for nearby places
    places_result = search_nearby_places(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius=radius,
        max_results=max_results
    )
    
    if not places_result["success"]:
        return {
            "success": False,
            "error": f"Places search failed: {places_result['error']}"
        }
    
    # Generate map URLs for the search location
    search_map_data = generate_map_url(location)
    
    # Prepare comprehensive response
    response = {
        "success": True,
        "search_query": {
            "location": location,
            "geocoded_address": geocode_result["formatted_address"],
            "coordinates": coords,
            "category_filter": category,
            "radius_meters": radius,
            "max_results": max_results
        },
        "results": {
            "total_found": places_result["total_results"],
            "places": places_result["places"]
        },
        "map_visualization": {
            "search_center_urls": search_map_data.get("map_urls", {}),
            "search_area_html": generate_places_map_html(
                latitude, longitude, places_result["places"], radius, location
            )
        }
    }
    
    # Add chat-friendly summary
    if places_result["places"]:
        place_names = [place["name"] for place in places_result["places"][:5]]
        summary = f"Found {places_result['total_results']} places"
        if category:
            summary += f" in category '{category}'"
        summary += f" within {radius}m of {geocode_result['formatted_address']}"
        if len(place_names) < places_result['total_results']:
            summary += f". Top results: {', '.join(place_names)}, and {places_result['total_results'] - len(place_names)} more."
        else:
            summary += f": {', '.join(place_names)}"
        
        response["chat_summary"] = summary
    else:
        response["chat_summary"] = f"No places found within {radius}m of {geocode_result['formatted_address']}"
        if category:
            response["chat_summary"] += f" matching category '{category}'"
    
    return response

@mcp.tool()
def reverse_geocode(latitude: float, longitude: float) -> Dict:
    """
    Reverse geocode coordinates to get address and location information
    
    Args:
        latitude: The latitude coordinate (e.g., 37.4419)
        longitude: The longitude coordinate (e.g., -122.1430)
        
    Returns:
        Reverse geocoded result with address and metadata
    """
    return reverse_geocode_coordinates(latitude, longitude)

@mcp.tool()
def get_elevation_for_coordinates(latitude: float, longitude: float) -> Dict:
    """
    Get elevation data for coordinates
    
    Args:
        latitude: The latitude coordinate (e.g., 37.4419)
        longitude: The longitude coordinate (e.g., -122.1430)
        
    Returns:
        Elevation data with coordinates and metadata
    """
    return get_elevation(latitude, longitude)

@mcp.tool()
def get_elevation_for_address(address: str) -> Dict:
    """
    Get elevation data for an address by first geocoding it
    
    Args:
        address: The address string to get elevation for
        
    Returns:
        Elevation data with coordinates and metadata
    """
    # First geocode the address
    geocode_result = geocode_address(address)
    if not geocode_result["success"]:
        return {
            "success": False,
            "address": address,
            "error": f"Failed to geocode address: {geocode_result['error']}",
            "elevation": None
        }
    
    # Get elevation for the geocoded coordinates
    coords = geocode_result["coordinates"]
    elevation_result = get_elevation(coords["latitude"], coords["longitude"])
    
    # Combine the results
    if elevation_result["success"]:
        return {
            "success": True,
            "address": address,
            "formatted_address": geocode_result["formatted_address"],
            "coordinates": coords,
            "elevation": elevation_result["elevation"],
            "data_source": elevation_result["data_source"],
            "geocoding_score": geocode_result["score"]
        }
    else:
        return {
            "success": False,
            "address": address,
            "formatted_address": geocode_result["formatted_address"],
            "coordinates": coords,
            "error": elevation_result["error"],
            "elevation": None
        }

@mcp.tool()
def get_directions(origin: str, destination: str, travel_mode: str = "driving") -> Dict:
    """
    Get directions and routing information between two locations
    
    Args:
        origin: The starting location (address or coordinates as "lat,lon")
        destination: The ending location (address or coordinates as "lat,lon")
        travel_mode: Transportation mode - "driving", "walking", or "trucking" (default: "driving")
        
    Returns:
        Dictionary containing routing result with step-by-step directions, travel time, distance, and formatted chat display
    """
    result = get_directions_between_locations(origin, destination, travel_mode)
    
    # Add formatted chat display to the result
    if "success" in result:
        result["formatted_directions"] = format_directions_for_chat(result)
    
    return result

def find_places_by_coordinates(latitude: float, longitude: float, category: Optional[str] = None, radius: int = 1000, max_results: int = 10) -> Dict:
    """
    Find nearby places around specific coordinates with optional category filtering
    
    Args:
        latitude: Latitude coordinate to search around
        longitude: Longitude coordinate to search around
        category: Optional category filter (e.g., 'restaurant', 'gas_station', 'park', 'hotel', 'hospital')
        radius: Search radius in meters (default: 1000m, max: 50000m)
        max_results: Maximum number of results to return (default: 10, max: 50)
        
    Returns:
        Dictionary containing nearby places with details and map visualization options
    """
    # Validate inputs
    radius = min(max(radius, 10), 50000)  # Clamp between 10m and 50km
    max_results = min(max(max_results, 1), 50)  # Clamp between 1 and 50
    
    # Search for nearby places
    places_result = search_nearby_places(
        latitude=latitude,
        longitude=longitude,
        category=category,
        radius=radius,
        max_results=max_results
    )
    
    if not places_result["success"]:
        return {
            "success": False,
            "error": f"Places search failed: {places_result['error']}"
        }
    
    # Get reverse geocoded address for the coordinates
    reverse_geocode_result = reverse_geocode_coordinates(latitude, longitude)
    location_description = f"{latitude:.4f}, {longitude:.4f}"
    if reverse_geocode_result["success"]:
        location_description = reverse_geocode_result["formatted_address"]
    
    # Prepare comprehensive response
    response = {
        "success": True,
        "search_query": {
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "location_description": location_description,
            "category_filter": category,
            "radius_meters": radius,
            "max_results": max_results
        },
        "results": {
            "total_found": places_result["total_results"],
            "places": places_result["places"]
        },
        "map_visualization": {
            "search_area_html": generate_places_map_html(
                latitude, longitude, places_result["places"], radius, location_description
            )
        }
    }
    
    # Add chat-friendly summary
    if places_result["places"]:
        place_names = [place["name"] for place in places_result["places"][:5]]
        summary = f"Found {places_result['total_results']} places"
        if category:
            summary += f" in category '{category}'"
        summary += f" within {radius}m of {location_description}"
        if len(place_names) < places_result['total_results']:
            summary += f". Top results: {', '.join(place_names)}, and {places_result['total_results'] - len(place_names)} more."
        else:
            summary += f": {', '.join(place_names)}"
        
        response["chat_summary"] = summary
    else:
        response["chat_summary"] = f"No places found within {radius}m of {location_description}"
        if category:
            response["chat_summary"] += f" matching category '{category}'"
    
    return response

@mcp.tool()
def generate_map_url(address: str, zoom_level: int = 15) -> Dict:
    """
    Generate map URLs for displaying geocoded locations in chat UI
    
    Args:
        address: The geocoded address to generate map for
        zoom_level: Map zoom level (default: 15)
        
    Returns:
        Dictionary containing various map service URLs
    """
    geocode_result = geocode_address(address)
    if not geocode_result["success"]:
        return {"error": f"Geocoding failed for {address}: {geocode_result['error']}"}
    
    coords = geocode_result["coordinates"]
    lat, lon = coords["latitude"], coords["longitude"]
    
    # Generate URLs for different map services
    map_urls = {
        "google_maps": f"https://www.google.com/maps?q={lat},{lon}&z={zoom_level}",
        "openstreetmap": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom={zoom_level}",
        "arcgis": f"https://www.arcgis.com/home/webmap/viewer.html?center={lon},{lat}&level={zoom_level}",
        "coordinates": f"{lat},{lon}",
        "formatted_address": geocode_result["formatted_address"]
    }
    
    return {
        "success": True,
        "address": address,
        "map_urls": map_urls,
        "embed_html": generate_map_embed_html(lat, lon, geocode_result["formatted_address"], zoom_level)
    }

def generate_places_map_html(center_lat: float, center_lon: float, places: list, radius: int, location_name: str) -> str:
    """Generate HTML for embedding a map showing nearby places in chat UI"""
    
    # Create markers for all places
    place_markers = ""
    for i, place in enumerate(places):
        lat = place["coordinates"]["latitude"]
        lon = place["coordinates"]["longitude"]
        name = place["name"].replace('"', '&quot;')
        
        # Different colors for different place types
        marker_color = "red" if i == 0 else "blue"
        
        place_markers += f"&marker={lat},{lon},color:{marker_color},label:{i+1}"
    
    # Calculate bounding box for the radius
    lat_offset = radius / 111000  # Rough conversion: 1 degree lat ≈ 111km
    lon_offset = radius / (111000 * abs(center_lat / 90))  # Adjust for latitude
    
    bbox = f"{center_lon-lon_offset},{center_lat-lat_offset},{center_lon+lon_offset},{center_lat+lat_offset}"
    
    return f"""
    <div style="width: 100%; height: 400px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden;">
        <iframe 
            width="100%" 
            height="100%" 
            frameborder="0" 
            scrolling="no" 
            marginheight="0" 
            marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&amp;layer=mapnik&amp;marker={center_lat},{center_lon}{place_markers}"
            title="Places near {location_name}">
        </iframe>
        <div style="padding: 8px; background: #f5f5f5; font-size: 12px;">
            <div style="font-weight: bold; margin-bottom: 4px;">📍 Places near {location_name}</div>
            <div style="margin-bottom: 4px;">🎯 Search Center: {center_lat:.4f}, {center_lon:.4f} (radius: {radius}m)</div>
            <div style="margin-bottom: 4px;">📊 Found {len(places)} places</div>
            <div style="max-height: 100px; overflow-y: auto;">
                {chr(10).join([f"<div style='margin: 2px 0;'>{i+1}. <strong>{place['name']}</strong> - {place['address'][:50]}{'...' if len(place['address']) > 50 else ''}</div>" for i, place in enumerate(places[:10])])}
            </div>
            <div style="margin-top: 4px;">
                <a href="https://www.google.com/maps?q={center_lat},{center_lon}" target="_blank" style="color: #1976d2;">View in Google Maps</a>
            </div>
        </div>
    </div>
    """

def generate_map_embed_html(lat: float, lon: float, address: str, zoom: int = 15) -> str:
    """Generate HTML for embedding a map in chat UI"""
    return f"""
    <div style="width: 100%; height: 300px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden;">
        <iframe 
            width="100%" 
            height="100%" 
            frameborder="0" 
            scrolling="no" 
            marginheight="0" 
            marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox={lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}&amp;layer=mapnik&amp;marker={lat},{lon}"
            title="Map showing {address}">
        </iframe>
        <div style="padding: 8px; background: #f5f5f5; font-size: 12px; text-align: center;">
            📍 {address} ({lat:.4f}, {lon:.4f})
            <br>
            <a href="https://www.google.com/maps?q={lat},{lon}" target="_blank" style="color: #1976d2;">View in Google Maps</a>
        </div>
    </div>
    """

@mcp.tool()
def display_location_on_map(address: str, include_html: bool = True, zoom_level: int = 15) -> Dict:
    """
    Complete tool for displaying a geocoded location on a map in the chat UI
    
    Args:
        address: The address to display on map
        include_html: Whether to include HTML embed code (default: True)
        zoom_level: Map zoom level (default: 15)
        
    Returns:
        Complete map display package including URLs and embed code
    """
    geocode_result = geocode_address(address)
    if not geocode_result["success"]:
        return {
            "success": False,
            "error": f"Failed to geocode address: {geocode_result['error']}"
        }
    
    map_data = generate_map_url(address, zoom_level)
    if "error" in map_data:
        return {"success": False, "error": map_data["error"]}
    
    coords = geocode_result["coordinates"]
    
    display_package = {
        "success": True,
        "address": address,
        "formatted_address": geocode_result["formatted_address"],
        "coordinates": coords,
        "map_urls": map_data["map_urls"],
        "geocoding_score": geocode_result["score"]
    }
    
    if include_html:
        display_package["embed_html"] = map_data["embed_html"]
        display_package["markdown_map"] = f"📍 **{geocode_result['formatted_address']}**\n\n🗺️ [View on Google Maps]({map_data['map_urls']['google_maps']})\n📐 Coordinates: `{coords['latitude']:.4f}, {coords['longitude']:.4f}`\n🎯 Accuracy Score: {geocode_result['score']}/100"
    
    return display_package

@mcp.tool()
def display_location_with_elevation(address: str, include_html: bool = True, zoom_level: int = 15) -> Dict:
    """
    Complete tool for displaying a geocoded location with elevation data in the chat UI
    
    Args:
        address: The address to display on map with elevation
        include_html: Whether to include HTML embed code (default: True)
        zoom_level: Map zoom level (default: 15)
        
    Returns:
        Complete display package including coordinates, elevation, URLs and embed code
    """
    # Get geocoding and elevation data
    elevation_result = get_elevation_for_address(address)
    if not elevation_result["success"]:
        return {
            "success": False,
            "error": f"Failed to get elevation for address: {elevation_result['error']}"
        }
    
    # Get map data
    map_data = generate_map_url(address, zoom_level)
    if "error" in map_data:
        return {"success": False, "error": map_data["error"]}
    
    coords = elevation_result["coordinates"]
    elevation = elevation_result["elevation"]
    
    display_package = {
        "success": True,
        "address": address,
        "formatted_address": elevation_result["formatted_address"],
        "coordinates": coords,
        "elevation": elevation,
        "map_urls": map_data["map_urls"],
        "geocoding_score": elevation_result.get("geocoding_score", 0)
    }
    
    if include_html:
        display_package["embed_html"] = map_data["embed_html"]
        display_package["markdown_map"] = f"📍 **{elevation_result['formatted_address']}**\n\n🗺️ [View on Google Maps]({map_data['map_urls']['google_maps']})\n📐 Coordinates: `{coords['latitude']:.4f}, {coords['longitude']:.4f}`\n⛰️ Elevation: `{elevation['meters']} m ({elevation['feet']} ft)`\n🎯 Accuracy Score: {elevation_result.get('geocoding_score', 0)}/100"
    
    return display_package

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# Add a geocoding resource for displaying location data
@mcp.resource("location://{address}")
def get_location_info(address: str) -> str:
    """Get location information for an address"""
    geocode_result = geocode_address(address)
    if geocode_result["success"]:
        coords = geocode_result["coordinates"]
        return f"Location: {geocode_result['formatted_address']}\nCoordinates: {coords['latitude']}, {coords['longitude']}\nScore: {geocode_result['score']}"
    else:
        return f"Geocoding failed for {address}: {geocode_result['error']}"

# Add a reverse geocoding resource for displaying address data from coordinates
@mcp.resource("reverse_geocode://{latitude},{longitude}")
def get_reverse_geocode_info(latitude: str, longitude: str) -> str:
    """Get address information for coordinates"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        reverse_result = reverse_geocode_coordinates(lat, lon)
        if reverse_result["success"]:
            address_components = reverse_result["address_components"]
            return f"Address: {reverse_result['formatted_address']}\nCoordinates: {lat}, {lon}\nStreet: {address_components['street']}\nCity: {address_components['city']}\nState: {address_components['state']}\nCountry: {address_components['country']}"
        else:
            return f"Reverse geocoding failed for {lat}, {lon}: {reverse_result['error']}"
    except ValueError:
        return f"Invalid coordinates: {latitude}, {longitude}"
    
# Add an elevation resource for displaying elevation data from coordinates
@mcp.resource("elevation://{latitude},{longitude}")
def get_elevation_info(latitude: str, longitude: str) -> str:
    """Get elevation information for coordinates"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        elevation_result = get_elevation(lat, lon)
        if elevation_result["success"]:
            elevation = elevation_result["elevation"]
            return f"Elevation at {lat}, {lon}:\n{elevation['meters']} meters ({elevation['feet']} feet)\nData source: {elevation_result['data_source']}"
        else:
            return f"Elevation lookup failed for {lat}, {lon}: {elevation_result['error']}"
    except ValueError:
        return f"Invalid coordinates: {latitude}, {longitude}"

# Add an elevation resource for addresses
@mcp.resource("elevation_address://{address}")
def get_elevation_address_info(address: str) -> str:
    """Get elevation information for an address"""
    elevation_result = get_elevation_for_address(address)
    if elevation_result["success"]:
        coords = elevation_result["coordinates"]
        elevation = elevation_result["elevation"]
        return f"Elevation for {elevation_result['formatted_address']}:\nCoordinates: {coords['latitude']}, {coords['longitude']}\nElevation: {elevation['meters']} meters ({elevation['feet']} feet)\nGeocoding Score: {elevation_result.get('geocoding_score', 0)}/100"
    else:
        return f"Elevation lookup failed for {address}: {elevation_result['error']}"


# Add a places resource for searching places near an address
@mcp.resource("places://{location}")
def get_places_near_location(location: str) -> str:
    """Get places information near a location"""
    places_result = find_places(location, max_results=10)
    if places_result["success"]:
        output = f"# Places near {location}\n\n"
        output += f"**Search Center:** {places_result['search_query']['geocoded_address']}\n"
        output += f"**Total Found:** {places_result['results']['total_found']} places\n\n"
        
        for i, place in enumerate(places_result['results']['places'][:10], 1):
            output += f"## {i}. {place['name']}\n"
            output += f"**Address:** {place['address']}\n"
            output += f"**Distance:** {place['distance']}m\n"
            if place['phone']:
                output += f"**Phone:** {place['phone']}\n"
            if place['website']:
                output += f"**Website:** {place['website']}\n"
            if place['categories']:
                output += f"**Categories:** {', '.join(place['categories'])}\n"
            output += "\n"
        
        return output
    else:
        return f"Failed to find places near {location}: {places_result['error']}"

# Add a places resource for searching places near coordinates
@mcp.resource("places://{latitude},{longitude}")
def get_places_near_coordinates(latitude: str, longitude: str) -> str:
    """Get places information near coordinates"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        places_result = find_places_by_coordinates(lat, lon, max_results=10)
        if places_result["success"]:
            output = f"# Places near {lat}, {lon}\n\n"
            output += f"**Location:** {places_result['search_query']['location_description']}\n"
            output += f"**Total Found:** {places_result['results']['total_found']} places\n\n"
            
            for i, place in enumerate(places_result['results']['places'][:10], 1):
                output += f"## {i}. {place['name']}\n"
                output += f"**Address:** {place['address']}\n"
                output += f"**Distance:** {place['distance']}m\n"
                if place['phone']:
                    output += f"**Phone:** {place['phone']}\n"
                if place['website']:
                    output += f"**Website:** {place['website']}\n"
                if place['categories']:
                    output += f"**Categories:** {', '.join(place['categories'])}\n"
                output += "\n"
            
            return output
        else:
            return f"Failed to find places near {lat}, {lon}: {places_result['error']}"
    except ValueError:
        return f"Invalid coordinates: {latitude}, {longitude}"

if __name__ == "__main__":
    # Start the server locally
    #mcp.run(transport="sse")
    mcp.run(transport="stdio")