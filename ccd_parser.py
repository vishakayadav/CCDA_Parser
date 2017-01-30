import xmltodict
from bs4 import BeautifulSoup as soup
import json
import traceback
from pprint import pprint

health_record = {}
health_record = {'demographics' : [{'title' : 'Demographics'}], 'encounters' : [{'title' : 'Encounters'}], 'medications' : [{'title' : 'Medications'}], 'allergies' : [{'title' : 'Allergies'}], 'procedures' : [{'title' : 'Procedures'}], 'results' : [{'title' : 'Results'}], 'vitals' : [{'title' : 'Vitals'}],'problems' : [{'title' : 'Problems'}], 'providers' : [{'title' : 'Providers'}]}

class ParsingCCD:
	ccdfile = ''
	def __init__(self, filename):
		self.ccdfile = filename 
		self.health_record = {
		'demographics' :[{'title' : 'Demographics'}], 
		'encounters' : [{'title' : 'Encounters'}], 
		'medications' : [{'title' : 'Medications'}], 
		'allergies' : [{'title' : 'Allergies'}], 
		'procedures' : [{'title' : 'Procedures'}], 
		'results' : [{'title' : 'Results'}], 
		'vitals' : [{'title' : 'Vitals'}],
		'problems' : [{'title' : 'Problems'}], 
		'providers' : [{'title' : 'Providers'}]
		}

	def writeToJSON(self):
		jsonfile = self.ccdfile.split(".")[0]
		with open(jsonfile+'.json', 'w') as f:
			json.dump(self.health_record, f, sort_keys = True, indent = 2)
		return (jsonfile+'.json')
		
	def parse(self):

		infile = open(self.ccdfile,"r")
		contents = infile.read()
		s = soup(contents,"lxml")
		elements = s.find_all('title')

		demo = {}
		document_id = s.find('id')['root']
		visit_id = None
		demo['title'] = s.find('title').get_text() 


############################################################################
# 								PROVIDERS
############################################################################
		try:
			providers = s.find_all("performer", typecode="PRF")
			if providers:
				for provider  in providers:
					providers_dict = {}   
					# provider_dict['title']="Providers"          
					obj = xmltodict.parse(provider.prettify())
					
					provider_type = obj['performer']['functioncode']['@code']
					if provider_type:
					
						try:
							providers_dict['provider_speciality'] = obj['performer']['assignedentity']['code']['@displayname']
						except:
							providers_dict['provider_speciality'] = None
						try:
							providers_dict['provider_npi'] = obj['performer']['assignedentity']['id']['@extension']
						except:
							providers_dict['provider_npi'] = None
						try:
							providers_dict['prefix'] = obj['performer']['assignedentity']['assignedperson']['name']['prefix']
							prefix = obj['performer']['assignedentity']['assignedperson']['name']['prefix']
						except:
							providers_dict['prefix'] = None
						try:
							name=obj['performer']['assignedentity']['assignedperson']['name']['given']
							if isinstance(name,list):
								providers_dict['prov_first_name']=name[0]
								providers_dict['prov_middle_name']=name[1]
							else:
								providers_dict['prov_first_name']=name
								providers_dict['prov_middle_name']=None
						except:
							providers_dict['prov_first_name']=None
							providers_dict['prov_middle_name']=None
						try:
							providers_dict['prov_last_name']  = obj['performer']['assignedentity']['assignedperson']['name']['family']
						except:
							providers_dict['prov_last_name']  = None

					self.health_record['providers'].append(providers_dict)

		except:
			pass
			


		          
######################################################################
#							DEMOGRAPHICS
######################################################################

		try:
			patientRole = s.find('patientrole')
			pid = patientRole.find('id')
			obj = xmltodict.parse(pid.prettify())
			demo['patient_id'] =obj['id']['@extension']
			demo['ccd_doc_id'] = document_id
			patient = patientRole.find('patient')
			obj = xmltodict.parse(patient.prettify())
			
			name=obj['patient']['name']['given']
			if isinstance(name,list):
				demo['first_name']=name[0]
				demo['middle_name']=name[1]
			else:
				demo['first_name']=name
				demo['middle_name']= None
			try:
				demo['last_name']=obj['patient']['name']['family']
			except Exception,e:
				demo['last_name'] = None
			try:
				demo['gender']=obj['patient']['administrativegendercode']['@code']
			except Exception,e:
				demo['gender'] = None
			try:
				demo['DOB']= obj['patient']['birthtime']['@value']
			except Exception,e:
				demo['DOB'] = None
			try:
				demo['race']=obj['patient']['racecode']['@displayname']
			except Exception,e:
				demo['race'] = None
			
		except:
			pass

#*********************Address***********************

		try:
			add = s.find("addr", use='HP')
			if not add:
				add = s.find('addr', use='WP')
			if add:
				obj = xmltodict.parse(add.prettify())
				if isinstance(obj['addr'],list):
					try:
						demo['mail_address1'] = obj['addr']['streetaddressline'][0]
						demo['mail_address2'] = obj['addr']['streetaddressline'][1]
					except:
						demo['mail_address1'] = None
						demo['mail_address2'] = None
				else:
					try:
						demo['mail_address1'] = obj['addr']['streetaddressline']
					except:
						demo['mail_address1'] = None
				try:
					demo['city']=obj['addr']['city']
				except Exception,e:
					demo['city'] = None
				try:
					demo['state']=obj['addr']['state']
				except Exception,e:
					demo['state'] = None
				try:
					demo['zip_code']=obj['addr']['postalcode']
				except Exception,e:
					demo['zip_code']=None
				try:
					demo['country']=obj['addr']['country']
				except Exception,e:
					demo['country'] = None
		except:
			pass



#************************* Phone *************************
		phn = s.find("telecom",use="HP")
		if phn:
			phone = phn['value']
			demo['primary_phone'] = phone.replace("tel:","")
		else:
			demo['primary_phone'] = None
			phn = s.find("telecom",use="WP")
			if phn:
				phone = phn['value']
				demo['secondary_phone'] = phone.replace("tel:","")
			else:
				demo['secondary_phone'] = None


		self.health_record['demographics'].append(demo)
			


		sections = s.find_all('section')
		for section in sections:



###########################################################################
#		 		PATIENT VISITS/ENCOUNTER ATTRIBUTES
###########################################################################				

			if section.find_all('code', attrs={'code':'46240-8'}):
				# problems = section.find_all('code', attrs={'code':'11450-4'})
				encounters = section.find_all('encounter', classcode="ENC")
				if encounters:
					for encounter in encounters:
						enc_dict = {}
						if encounter:
							obj = xmltodict.parse(encounter.prettify())
							try:
								enc_dict['enc_code'] = obj['encounter']['code']['@code']
								if enc_dict['enc_code']:
									try:
										enc_dict['enc_coding_system'] = obj['encounter']['code']['@codesystemname']
									except:
										enc_dict['enc_coding_system'] = None    
									try:
										enc_dict['enc_description'] = obj['encounter']['code']['originaltext']['#text']
									except:
										enc_dict['enc_description'] = None
									try:
										enc_dict['enc_place'] = obj['encounter']['participant']['participantrole']['playingentity']['name']
									except:
										enc_dict['enc_place'] = None
									try:
										enc_dict['enc_date'] = obj['encounter']['effectivetime']['@value']
									except:
										enc_dict['enc_date'] = None
									try:
										enc_dict['enc_result'] = obj['encounter']['entryrelationship'][0]['observation']['value']['@displayname']
									except:
										print traceback.format_exc()
										enc_dict['enc_result'] = None
								else:
									print traceback.format_exc()	
								
							except Exception,e:
								print traceback.format_exc()
							
						else:
							pass
						self.health_record['encounters'].append(enc_dict)
								

##########################################################################
#							MEDICATIONS
##########################################################################

			medications = section.find('code', attrs={'code':'10160-0'})
			if medications:
				med_codeSystem = medications.parent.find('code').get('codesystemname')
				if medications.parent.find('tbody'):
					for medication in medications.parent.find('tbody').findAll('tr'):
						med_dict={}
						try:
							obj = xmltodict.parse(medication.prettify())
							try:
								med_dict['medication']=obj['tr']['td'][0]["content"]['#text']
							except Exception,e:
								med_dict['medication']=None
							try:
								med_dict['dose_directions']=obj['tr']['td'][1].split(',')[1]
							except Exception,e:
								med_dict['dose_directions'] = None
							try:
								med_dict['indications']=obj['tr']['td'][4]
							except Exception,e:
								med_dict['indications'] = None					
							try:
								med_dict['instructions']=obj['tr']['td'][5]['content']['#text']
							except Exception,e:
								med_dict['instructions'] = None
							try:
								med_dict['med_status']=obj['tr']['td'][3]
							except Exception,e:
								med_dict['med_status'] = None
							try:
								med_dict['start_date']=obj['tr']['td'][2]
							except Exception,e:
								med_dict['start_date'] = None


							try:
								med_dict['administration_route']=obj['tr']['td'][1].split(' ')[2]
							except Exception,e:
								med_dict['administration_route'] =  None
							
							med_dict['med_coding_system']=med_codeSystem
							med_dict['med_ccd_doc_id'] = data['ccd_doc_id']
						except:
							pass
						self.health_record['medications'].append(med_dict)





#########################################################################
#						ALLERGIES/ALERTS
#########################################################################

			allergies = section.find('code', attrs={'code':'48765-2'})
			if allergies:
				if allergies.parent.find('tbody'):
					for allergy in allergies.parent.find('tbody').findAll('tr'):
						allergy_dict={}
						try:
							obj = xmltodict.parse(allergy.prettify())
							try:
								allergy_dict['substance']=obj['tr']['td'][0]
							except Exception,e:
								allergy_dict['substance']=None
							try:
								allergy_dict['reaction']=obj['tr']['td'][1]['content']['#text']
							except Exception,e:
								allergy_dict['reaction'] = None
							try:
								allergy_dict['severity']=obj['tr']['td'][2]['content']['#text']
							except Exception,e:
								allergy_dict['severity'] = None
							try:
								allergy_dict['allergy_status']=obj['tr']['td'][3]
							except Exception,e:
								allergy_dict['allergy_status'] = None
							
							allergy_dict['allergy_ccd_doc_id'] = data['ccd_doc_id']
						except:
							pass
						self.health_record['allergies'].append(allergy_dict)





###################################################################
#							PROCEDURES
###################################################################

			procedures = section.find('code',code='47519-4')
			if procedures: 
				procedure= procedures.parent.find_all('procedure', classcode="PROC")
				if procedure:
					for proce in procedure:
						proc_dict={}
						try:
							obj = xmltodict.parse(proce.prettify())
							try:
								proc_dict['procedure_code']=obj['procedure']['code']['@code']
							except:
								proc_dict['procedure_code'] = None
							try:
								proc_dict['proc_code_system']=obj['procedure']['code']['@codesystemname']
							except:
								proc_dict['proc_code_system']=None
							try:
								proc_dict['procedure_name']=obj['procedure']['code']['@displayname']
							except:
								proc_dict['procedure_name']=None
							try:
								proc_dict['procedure_date']=obj['procedure']['effectivetime']['@value']
							except Exception,e:
								proc_dict['procedure_date'] = None
							try:
								proc_dict['place_of_service_code'] = obj['procedure']['participant']['participantrole']['code']['@code']
							except:
								proc_dict['place_of_service_code']=None
							try:
								proc_dict['place_of_service_codesystem'] = obj['procedure']['participant']['participantrole']['code']['@codesystemname']
							except:
								proc_dict['place_of_service_codesystem']=None
							try:
								proc_dict['place_of_service'] = obj['procedure']['participant']['participantrole']['playingentity']['name']
							except:
								proc_dict['place_of_service']=None
						except:
							print traceback.format_exc()
						self.health_record['procedures'].append(proc_dict)



#######################################################################
#              		        RESULTS
#######################################################################

			results = section.find('code', attrs={'code':'30954-2'})
			if results:
				result = results.parent.find_all('observation', classcode="OBS")
				if result:
					for res in result:
						res_dict = {}
						obj = xmltodict.parse(res.prettify())
						try:
							res_dict['test_code'] = obj['observation']['code']['@code']
							if res_dict['test_code']:
								try:
									res_dict['test_coding_system'] = obj['observation']['code']['@codesystemname']
								except:
									res_dict['test_coding_system'] = None    
								try:
									res_dict['test_name'] = obj['observation']['code']['@displayname']
								except:
									res_dict['test_name'] = None
								try:
									res_dict['test_measuring_unit'] = obj['observation']['value']['@unit']
								except:
									res_dict['test_measuring_unit'] = None
								if res_dict['test_measuring_unit'] is not None:
									try:    
										res_dict['test_result'] = obj['observation']['value']['@value']
									except:
										print traceback.format_exc()
										res_dict['test_result'] = None
									try:    
										res_dict['test_result_comment'] = obj['observation']['interpretationcode']['@code']
									except:
										res_dict['test_result_comment'] = None
								else:
									res_dict['test_result'] = None
									res_dict['test_result_comment'] = None
								try:
									res_dict['reference_highvalue_male'] = obj['observation']['referencerange']['observationrange']['value']['high']['@value']
									res_dict['reference_highvalue_female'] = res_dict['reference_highvalue_male']
								except:
									try:
										res_dict['reference_highvalue_male'] = obj['observation']['referencerange']['observationrange']['text'].split("; ")[0].split(" ")[1].split("-")[1]
										res_dict['reference_highvalue_female'] = obj['observation']['referencerange']['observationrange']['text'].split("; ")[1].split(" ")[1].split("-")[1]							
									except:
										res_dict['reference_highvalue_male'] = None
										res_dict['reference_highvalue_female'] = None
								try:
									res_dict['reference_lowvalue_male'] = obj['observation']['referencerange']['observationrange']['value']['low']['@value']
									res_dict['reference_lowvalue_female'] = res_dict['reference_lowvalue_male']
								except:
									try:
										res_dict['reference_lowvalue_male'] = obj['observation']['referencerange']['observationrange']['text'].split("; ")[0].split(" ")[1].split("-")[0]
										res_dict['reference_lowvalue_female'] = obj['observation']['referencerange']['observationrange']['text'].split("; ")[1].split(" ")[1].split("-")[0]							
									except:
										res_dict['reference_lowvalue_male'] = None
										res_dict['reference_lowvalue_female'] = None
								try:
									res_dict['test_date'] = obj['observation']['effectivetime']['@value']
								except:
									res_dict['test_date'] = None
								
							self.health_record['results'].append(res_dict)
							
						except Exception,e:
							print traceback.format_exc()
						
				else:
					pass




#############################################################################
#								VITALS
#############################################################################
			vitals = section.find('code', attrs={'code':'8716-3'})
			if vitals:
				vital = vitals.parent.find_all('organizer', classcode="CLUSTER")
				if vital:
					for vtl in vital:
						obj_date = xmltodict.parse(vtl.prettify())
						vtl_components = vtl.find_all('observation', classcode = 'OBS')
						if vtl_components:
							for vtl_component in vtl_components:
								vital_dict = {}
								try:
									vital_dict['observation_date'] = obj_date['organizer']['effectivetime']['@value']
								except:
									vital_dict['observation_date'] = None
								
								obj = xmltodict.parse(vtl_component.prettify())
								try:
									vital_dict['vtl_code'] = obj['observation']['code']['@code']
									if vital_dict['vtl_code']:
										try:
											vital_dict['vtl_coding_system'] = obj['observation']['code']['@codesystemname']
										except:
											vital_dict['vtl_coding_system'] = None    
										try:
											vital_dict['vtl_name'] = obj['observation']['code']['@displayname']
										except:
											vital_dict['vtl_name'] = None
										try:
											vital_dict['vtl_measuring_unit'] = obj['observation']['value']['@unit']
										except:
											vital_dict['vtl_measuring_unit'] = None
										if vital_dict['vtl_measuring_unit'] is not None:
											try:    
												vital_dict['vtl_result'] = obj['observation']['value']['@value']
											except:
												print traceback.format_exc()
												vital_dict['vtl_result'] = None
											try:    
												vital_dict['vtl_result_comment'] = obj['observation']['interpretationcode']['@code']
											except:
												vital_dict['vtl_result_comment'] = None
										else:
											vital_dict['vtl_result'] = None
											vital_dict['vtl_result_comment'] = None
										
									self.health_record['vitals'].append(vital_dict)
									
								except Exception,e:
									print traceback.format_exc()


############################################################################
#                 		     PROBLEMS
############################################################################

			if section.find_all('code', attrs={'code':'11450-4'}):
				problems = section.find_all('act', classcode="ACT")
				if problems:
					for problem in problems:
						prob_dict = {}
						prob=problem.find('observation', classcode="OBS")
						obj = xmltodict.parse(prob.prettify())
						try:
							prob_dict['prob_code'] = obj['observation']['value']['@code']
							if prob_dict['prob_code']:
								try:
									prob_dict['prob_coding_system'] = obj['observation']['value']['@codesystem']
								except:
									prob_dict['prob_coding_system'] = None    
								try:
									prob_dict['prob_description'] = obj['observation']['value']['@displayname']
								except:
									prob_dict['prob_description'] = None
								try:    
									status_code = problem.find('code', code = '33999-4').parent
									obj1 = xmltodict.parse(status_code.prettify())
									status = obj1['observation']['value']['@displayname']
									prob_dict['prob_status'] = status	
								except:
									prob_dict['prob_status'] = None
								try:
									prob_dict['problem_since'] = obj['observation']['effectivetime']['low']['@value']
								except:
									prob_dict['problem_since'] = None

							self.health_record['problems'].append(prob_dict)

						except Exception,e:
							print traceback.format_exc()
						
				else:
					pass
		self.writeToJSON()
		x = self.writeToJSON()
 		return x
