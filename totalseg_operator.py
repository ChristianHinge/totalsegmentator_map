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

from monai.deploy.core import Fragment, Operator, OperatorSpec
from monai.transforms.spatial.functional import orientation
from monai.deploy.core import Image

from skimage.filters import median
import numpy as np
from monai.transforms import SaveImage
import nibabel as nib
import shutil
import tempfile
import subprocess
import json 
from totalseg_pdf import generate_pdf_report
# If `pip_packages` is specified, the definition will be aggregated with the package dependency list of other
# operators and the application in packaging time.
# @md.env(pip_packages=["scikit-image >= 0.17.2"])

class TotalsegmentatorPDFOperator(Operator):
    """This Operator implements a noise reduction.

    The algorithm is based on the median operator.
    It ingests a single input and provides a single output, both are in-memory image arrays
    """

    def setup(self, spec: OperatorSpec):
        spec.input("report_dict")
        spec.output("pdf_bytes")

    def compute(self, op_input, op_output, context):
            
        report_dict = op_input.receive("report_dict")
        pdf_bytes = generate_pdf_report(report_dict)
        op_output.emit(pdf_bytes, "pdf_bytes")

class TotalsegmentatorOperator(Operator):
    """This Operator implements a noise reduction.

    The algorithm is based on the median operator.
    It ingests a single input and provides a single output, both are in-memory image arrays
    """

    # Define __init__ method with super().__init__() if you want to override the default behavior.
    def __init__(self, fragment: Fragment, *args, **kwargs):
        """Create an instance to be part of the given application (fragment).

        Args:
            fragment (Fragment): The instance of Application class which is derived from Fragment
        """

        # Need to call the base class constructor last
        super().__init__(fragment, *args, **kwargs)
    
    def setup(self, spec: OperatorSpec):
        spec.input("study_selected_series_list")
        spec.output("report_dict")

    def compute(self, op_input, op_output, context):

        data_in = op_input.receive("study_selected_series_list")

        with tempfile.TemporaryDirectory() as temp:
            print(f"Copying DICOM Instances...")
            for idx, f in enumerate(data_in[0].selected_series[0].series.get_sop_instances()):
                dcm_filepath = f._sop.filename
                shutil.copy2(dcm_filepath, temp)
            
            print("Running TotalSegmentator...")
            in_dir = str(temp)
            out_dir = in_dir + "/out"
            cmd = f"TotalSegmentator -f --roi_subset spleen --statistics --body_seg -i {in_dir} -o {out_dir}"
            subprocess.check_output(cmd.split(" "))
            js = out_dir + "/statistics.json"
            #js = "/home/pet/monai-deploy-app-sdk/examples/apps/simple_imaging_app/seg/statistics.json"
            with open(js,"r") as handle:
               report = json.load(handle)

        op_output.emit(report, "report_dict")

