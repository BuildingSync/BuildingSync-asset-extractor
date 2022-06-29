"""
*********************************************************************************************************
:copyright (c) BuildingSync®, Copyright (c) 2015-2022, Alliance for Sustainable Energy, LLC,
and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

(1) Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

(2) Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the distribution.

(3) Neither the name of the copyright holder nor the names of any contributors may be used to endorse
or promote products derived from this software without specific prior written permission from the
respective party.

(4) Other than as required in clauses (1) and (2), distributions in any form of modifications or other
derivative works may not use the "BuildingSync" trademark or any other confusingly similar designation
without specific prior written permission from Alliance for Sustainable Energy, LLC.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER(S) AND ANY CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER(S), ANY
CONTRIBUTORS, THE UNITED STATES GOVERNMENT, OR THE UNITED STATES DEPARTMENT OF ENERGY, NOR ANY OF
THEIR EMPLOYEES, BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*********************************************************************************************************
"""
import os

from buildingsync_asset_extractor.processor import BSyncProcessor

# import glob
# from pathlib import Path


# # 1: regular test
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests/files/completetest.xml')
out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets_output.json')
out_file2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets_output2.json')

print("filename: {}".format(filename))

# bp = BSyncProcessor(filename=filename, logger_level='DEBUG')
bp = BSyncProcessor(filename=filename)
bp.extract()
bp.save(out_file)

# does it work when already loaded?
with open(filename, mode='rb') as file:
    file_data = file.read()

bp = BSyncProcessor(data=file_data)
bp.extract()
bp.save(out_file2)

# 2: bigger test
# bae_tester_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'Desktop/BAE-tester/20220519_AT_BSXML')
# find_path = os.path.join(bae_tester_dir, '*', '*.xml')

# for file in glob.glob(find_path):
# 	print(file)
# 	out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', Path(file).stem + '.json')
# 	bp = BSyncProcessor(filename=file, logger_level='DEBUG')
# 	bp.extract()
# 	bp.save(out_file)

# 3: schema examples test
# bae_tester_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bsync-schema', 'examples')
# find_path = os.path.join(bae_tester_dir, '*.xml')

# for file in glob.glob(find_path):
# 	print(file)
# 	out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', Path(file).stem + '.json')
# 	bp = BSyncProcessor(filename=file, logger_level='DEBUG')
# 	bp.extract()
# 	bp.save(out_file)
