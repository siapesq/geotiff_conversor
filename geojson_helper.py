from logzero import logger
from geojson import Point,FeatureCollection,dump,Feature,Polygon,MultiPoint,MultiPolygon
from turfpy import measurement
from turfpy.transformation import convex
#ignore shapely warnings
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 

def create_point_feature(cordinates:tuple[2],properties:dict)->Feature:
    try:
        ponto=Point(coordinates=cordinates)
        feature=Feature(geometry=ponto,properties=properties)
        return feature
    except Exception as err:
        raise Exception(err)
    
def create_polygon(cordinates:list[list[2]],properties:dict)->Feature:
    try:
        polygon=Polygon(coordinates=cordinates)
        feature=Feature(geometry=polygon,properties=properties)
        return feature
    except Exception as err:
        raise Exception(err)

def create_multipoint(cordinates:list[list],properties:dict)->Feature:
    try:
        pontos=MultiPoint(coordinates=cordinates)
        feature=Feature(geometry=pontos,properties=properties)
        return feature
    except Exception as err:
        raise Exception(err)

def create_polygon_properties(color:str)->dict:
    try:
        return{
            "fill":color,
            "stroke-width": 0,
            "stroke-opacity": 0,
            "fill-opacity": 1
        }
    except Exception as err:
        raise Exception(err)
    
def create_multipolygon(cordinates:list[list],properties:dict)->Feature:
    try:
        multipolygon=MultiPolygon(coordinates=cordinates)
        feature=Feature(
            geometry=multipolygon,
            properties=properties
        )
        return feature
    except Exception as err:
        raise Exception(err)

def write_geojson(geojson_name:str,features:list[Feature]):
    try:
        logger.info(f"Dumping GeoJSON to Output File {geojson_name}")
        geojson=FeatureCollection(features=features)
        with open(geojson_name, 'w') as outfile:
            dump(geojson,outfile)
    except Exception as err:
        raise Exception(err)
    
def build_geojson(
    geojson_name:str,
    points:list[list[dict[str]]],
    min_channel_color:int,
    max_distance_between_points:int
):
    try:
        logger.info(f"Init GeoJSON Building")
        features=[]
        for r in range(min_channel_color,256):
            for g in range(min_channel_color,256):
                coords_same_color=points[r][g]['coords']
                if len(coords_same_color)==0:
                    continue
                polygons_coordinates=[]
                for index in range(0,len(coords_same_color)):
                    current_point=Point(coords_same_color[index])
                    polygon_coords=[coords_same_color[index]]
                    if index==len(coords_same_color)-1:
                        break
                    for next_index in range(index+1,len(coords_same_color)):
                        next_point=Point(coords_same_color[next_index])
                        distance=measurement.distance(point1=current_point,point2=next_point,units='km')
                        if distance<=max_distance_between_points:
                            polygon_coords.append(coords_same_color[next_index])
                        else:
                            polygon_coords.append(coords_same_color[index])
                            break
                    if len(polygon_coords)>=4:
                        p=[]
                        for c in polygon_coords:
                            feature=Feature(
                                geometry=Point(coordinates=c)
                            )
                            p.append(feature)
                        feature=convex(features=FeatureCollection(p))
                        convex_coordinates=feature['geometry']['coordinates']
                        if type(convex_coordinates[0][0])==list:
                            polygons_coordinates.append(convex_coordinates)

                if len(polygons_coordinates)>0:
                    #create MultiPolygon
                    color=points[r][g]['color']
                    multipolygon=MultiPolygon(coordinates=polygons_coordinates)
                    feature=Feature(
                        geometry=multipolygon,
                        properties={
                            "fill":color,
                            "stroke-width": 0,
                            "stroke-opacity": 0,
                            "fill-opacity": 1
                        }
                    )
                    features.append(feature)
                #feature=create_multipoint(
                #    cordinates=coords,
                #    properties={
                #        "marker-color":color
                #    }
                #)
                #features.append(feature)
        write_geojson(geojson_name=geojson_name,features=features)
        logger.info(f"Number of features in GeoJSON {len(features)}")

    except Exception as err:

        raise Exception(err)
    
