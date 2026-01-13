"""Internal types used to represent arguments to the API."""
from __future__ import annotations

import datetime
from typing import Any as AnyType, Dict, List as ListType, Sequence, Tuple, Union

from le import classifier
from le import clusterer
from le import computedobject
from le import confusionmatrix
from le import daterange
from le import dictionary
from le import ee_array
from le import ee_date
from le import ee_list
from le import ee_number
from le import ee_string
from le import element
from le import errormargin
from le import featurecollection
from le import filter as ee_filter
from le import image
from le import imagecollection
from le import kernel
from le import projection
from le import reducer

Array = Union[
    AnyType,
    ListType[AnyType],
    ee_array.Array,
    ee_list.List,
    computedobject.ComputedObject,
]
Bool = Union[bool, AnyType, computedobject.ComputedObject]
Classifier = Union[classifier.Classifier, computedobject.ComputedObject]
Clusterer = Union[clusterer.Clusterer, computedobject.ComputedObject]
ConfusionMatrix = Union[
    confusionmatrix.ConfusionMatrix, computedobject.ComputedObject
]
Date = Union[
    datetime.datetime, float, str, ee_date.Date, computedobject.ComputedObject
]
DateRange = Union[daterange.DateRange, computedobject.ComputedObject]
Dictionary = Union[
    Dict[AnyType, AnyType],
    Sequence[AnyType],
    dictionary.Dictionary,
    computedobject.ComputedObject,
]
Any = Union[AnyType, computedobject.ComputedObject]
Element = Union[AnyType, element.Element, computedobject.ComputedObject]
ErrorMargin = Union[
    float,
    ee_number.Number,
    errormargin.ErrorMargin,
    computedobject.ComputedObject,
]
FeatureCollection = Union[
    AnyType, featurecollection.FeatureCollection, computedobject.ComputedObject
]
Filter = Union[ee_filter.Filter, computedobject.ComputedObject]
Geometry = Union[AnyType, computedobject.ComputedObject]
Image = Union[AnyType, image.Image, computedobject.ComputedObject]
ImageCollection = Union[
    AnyType, imagecollection.ImageCollection, computedobject.ComputedObject
]
Integer = Union[int, ee_number.Number, computedobject.ComputedObject]
Kernel = Union[kernel.Kernel, computedobject.ComputedObject]
List = Union[
    ListType[AnyType],
    Tuple[()],
    Tuple[AnyType, AnyType],
    ee_list.List,
    computedobject.ComputedObject,
]
Number = Union[float, ee_number.Number, computedobject.ComputedObject]
Projection = Union[
    str,
    ee_string.String,
    projection.Projection,
    computedobject.ComputedObject,
]
Reducer = Union[reducer.Reducer, computedobject.ComputedObject]
String = Union[str, ee_string.String, computedobject.ComputedObject]
