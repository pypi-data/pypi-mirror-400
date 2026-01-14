import numpy as np
import os
import epicure.epicuring as epi

def test_load_movie():
    """ Read a standard tif movie """
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    assert epic.img.shape == (11,189,212)
    return

def test_load_image():
    """ Read a single image and a cellpose (labels) segmentation """
    test_img = os.path.join(".", "test_data", "static_image.tif")
    test_seg = os.path.join(".", "test_data", "static_image_cellpose.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    assert epic.img.shape == (1,507,585)
    epic.load_segmentation(test_seg)
    assert epic.seg.shape == epic.img.shape
    assert np.max(epic.seg) == 706
    return

def test_load_movie_with_chanel():
    """ Read a tif movie with 2 channels """
    test_img = os.path.join(".", "test_data", "area3_Composite.tif")
    test_seg = os.path.join(".", "test_data", "area3_Composite_epyseg.tif")
    epic = epi.EpiCure()
    resaxis, resval = epic.load_movie(test_img)
    # check the dimensions are correctly loaded
    assert epic.img.shape == (5,2,146,228)
    assert resaxis == 1
    assert resval == 2
    ## check the channels are correctly set
    assert np.mean(epic.img)>=150
    epic.set_chanel(1, 1)
    assert np.mean(epic.img)<150
    assert np.mean(epic.img)>100
    return

def test_load_segmentation():
    test_seg = os.path.join(".", "test_data", "003_crop_epyseg.tif")
    epic = epi.EpiCure()
    epic.load_segmentation(test_seg)
    assert epic.seg.shape == (11,189,212)
    assert np.max(epic.seg) == 1294
    return

def test_suggest():
    """ Check segmentation file name suggestion """
    ## case 1: file doesn't exists, creates it
    test_img = os.path.join(".", "test_data", "003_crop.tif")
    epic = epi.EpiCure()
    epic.load_movie(test_img)
    segfile = epic.suggest_segfile("epics")
    assert segfile is None
    ## case 2: if it exists, find it automatically
    test_img = os.path.join(".", "test_data", "013_crop.tif")
    epic.load_movie(test_img)
    segfile = epic.suggest_segfile("epics")
    resfile = os.path.join(".", "test_data", "epics", "013_crop_labels.tif")
    absp = os.path.abspath(resfile)
    assert segfile == absp 
    return

def test_init_epic():
    epic = epi.EpiCure()
    assert epic.img is None
    return

if __name__ == "__main__":
    test_load_movie()
    test_load_image()
    test_suggest()
    print("********* Test basics completed ***********")
