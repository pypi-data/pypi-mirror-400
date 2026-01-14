"""
Test the "export to trackmate XML" options in Output. 
Corresponding code in src/epicure/trackmate_export.py
"""

import epicure.epicuring as epicure
import os

def test_export_trackmate():
    """ Export tracks as a TrackMate XML file """
    raw_path = os.path.join( ".", "test_data", "013_crop.tif" )
    xml_path = os.path.join(".", "test_data", "epics", "013_crop.xml")
    if os.path.exists(xml_path):
        os.remove(xml_path)

    epic = epicure.EpiCure()
    epic.verbose = 3  # 0: minimal to 3: debug informations
    epic.load_movie(raw_path)
    epic.go_epicure(outdir="epics")

    epic.outputing.output_mode.setCurrentText("All cells")
    epic.outputing.save_tm_xml()

    ## check that metadata were well read
    assert epic.epi_metadata["ScaleXY"]==0.2
    assert int(epic.epi_metadata["ScaleT"])==300 
    ## check that TrackMate file was generated
    assert os.path.exists(xml_path)

if __name__ == "__main__":
    test_export_trackmate()
    print("********* Test export to TrackMate XML completed ***********")