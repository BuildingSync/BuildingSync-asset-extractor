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

from buildingsync_preimporter.processor import BSyncProcessor

filename = 'tests/files/testfile.xml'
# out_file = 'assets_output.json'

# filename = 'ASHRAE 211 Export.xml'  															# !!! doesn't work: no 'auc:' prefixes
# filename ='AT_example_AS_conversion_audit_report.xml'							# !!! works
# filename ='AT_example_NYC_audit_report_property.xml'							# !!! works
# filename ='AT_example_SF_audit_report.xml'												# !!! works
# filename ='BuildingSync Website Invalid Schema.xml'								# !!! works (nothing returned)
# filename ='BuildingSync Website Valid Schema.xml'									# !!! works (nothing returned)
# filename ='CMS Woodlawn Campus.xml'																# !!! doesn't work: no 'auc:' prefixes
# filename ='DC GSA Headquarters.xml'																# !!! doesn't work: no 'auc:' prefixes
# filename ='Golden Test File.xml'																	# !!! doesn't work: no 'auc:' prefixes
# filename ='LL87.xml' 																							# !! !doesn't work: no 'auc:' prefixes
# filename ='Multi-Facility Shared Systems.xml' 										# !!! doesn't work: no 'auc:' prefixes
# filename ='Multi_building_gbxml_externalreference_geometry.xml' 	# !!! doesn't work: no 'auc:' prefixes
# filename ='MultitenantBySubsections.xml'													# !!! doesn't work: no 'auc:' prefixes
# filename ='NIST Gaithersburg Campus.xml'													# !!! doesn't work: no 'auc:' prefixes
# filename ='Norfolk Federal Building.xml'													# !!! doesn't work: no 'auc:' prefixes
# filename ='Reference Building - Primary School.xml'								# !!! doesn't work: no 'auc:' prefixes
# filename ='Richmond Federal Building.xml'													# !!! doesn't work: no 'auc:' prefixes
# filename ='Single_building_gbxml_externalreference_geometry.xml'  # !!! doesn't work: no 'auc:' prefixes

out_file = 'output/' + os.path.basename(os.path.splitext(os.path.basename(filename))[0]) + '.json'

filename = '../bsync-schema/examples/' + filename
print("filename: {}".format(filename))

bp = BSyncProcessor(filename)
bp.extract()
bp.save(out_file)
