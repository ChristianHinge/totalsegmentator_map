# Copyright 2021 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from pathlib import Path

from gaussian_operator import GaussianOperator
from totalseg_operator import TotalsegmentatorOperator, TotalsegmentatorPDFOperator
from sobel_operator import SobelOperator

from monai.deploy.conditions import CountCondition
from monai.deploy.core import AppContext, Application
from monai.deploy.operators import DICOMSeriesSelectorOperator
from monai.deploy.operators import DICOMSeriesToVolumeOperator
from monai.deploy.operators import DICOMDataLoaderOperator
from monai.deploy.operators import DICOMEncapsulatedPDFWriterOperator
from monai.deploy.core import Image
from monai.deploy.operators import ModelInfo
# Decorator support is not available in this version of the SDK, to be re-introduced later
# @resource(cpu=1)
# @env(pip_packages=["scikit-image >= 0.17.2"])
class App(Application):
    """This is a very basic application.

    This showcases the MONAI Deploy application framework.
    """

    # App's name. <class name>('App') if not specified.
    name = "simple_imaging_app"
    # App's description. <class docstring> if not specified.
    description = "This is a very simple application."
    # App's version. <git version tag> or '0.0.0' if not specified.
    version = "0.1.0"

    def compose(self):
        """This application has three operators.

        Each operator has a single input and a single output port.
        Each operator performs some kind of image processing function.
        """

        # Use Commandline options over environment variables to init context.
        app_context: AppContext = Application.init_app_context(self.argv)
        sample_data_path = Path(app_context.input_path)
        output_data_path = Path(app_context.output_path)

        model_info = ModelInfo("J. Wasserthal","TotalSegmentator","0.0.1","")

        # Please note that the Application object, self, is passed as the first positional argument
        # and the others as kwargs.
        # Also note the CountCondition of 1 on the first operator, indicating to the application executor
        # to invoke this operator, hence the pipeline, only once.
    
        loader = DICOMDataLoaderOperator(self,CountCondition(self,1),input_folder=sample_data_path,name="dicom_loader")
        
        selector = DICOMSeriesSelectorOperator(self, name="series_selector")
        pdf_to_dcm = DICOMEncapsulatedPDFWriterOperator(self,name="pdf_dcm_encapsulator",output_folder=output_data_path,model_info=model_info,custom_tags={"SeriesDescription":"TotalSegmentator Report: Organ volumes"})
        totalseg_op = TotalsegmentatorOperator(self, name="totalseg_op")
        pdf_op = TotalsegmentatorPDFOperator(self,name="totalseg_pdf_op")

        self.add_flow(loader,selector,{("dicom_study_list","dicom_study_list")})
        self.add_flow(selector,totalseg_op,{("study_selected_series_list","study_selected_series_list")})
        self.add_flow(totalseg_op,pdf_op,{("report_dict","report_dict")})
        self.add_flow(selector,pdf_to_dcm,{("study_selected_series_list","study_selected_series_list")})
        self.add_flow(pdf_op,pdf_to_dcm,{("pdf_bytes","pdf_bytes")})

Rules_Text = """
{
    "selections": [
        {
            "name": "CT Series",
            "conditions": {
                "Modality": "CT"
            }
        }
    ]
}
"""

if __name__ == "__main__":
    logging.info(f"Begin {__name__}")
    App().run()
    logging.info(f"End {__name__}")
