import os
import libifcb
from datetime import datetime, timezone
import csv
import json
import re
import zipfile
import io
import time

csv.field_size_limit(1024 * 1024 * 1024)

class IFCBEntryProvider:
    def __init__(self, roi_readers, ifcb_ids, job_object, with_images = True, options = {}):
        self.roi_readers = roi_readers
        self.ifcb_ids = ifcb_ids
        self.with_images = with_images
        self.job_object = job_object
        self.reader_index = 0
        self.index = 0
        self.options = options
        self.column_sources = {}
        self.match_data_keys = {}
        self.process_time = datetime.now().replace(tzinfo=timezone.utc)

        self.ecotaxa_table_header = {
                "object_id": "[t]",
                "object_date": "[t]",
                "object_time": "[t]",
                "object_roi_width": "[f]",
                "object_roi_height": "[f]",
                "process_id": "[t]",
                "process_date": "[t]",
                "process_time": "[t]",
                "process_pixel_um": "[f]",
                "process_feature_extractor": "[t]",
                "acq_id": "[t]",
                "acq_operator": "[t]",
                "acq_instrument": "[t]",
                "acq_sn": "[t]",
                "acq_run_time": "[f]",
                "acq_grab_time_start": "[f]",
                "acq_trigger_number": "[f]",
                "acq_peak_a": "[f]",
                "acq_pmt_a": "[f]",
                "acq_peak_b": "[f]",
                "acq_pmt_b": "[f]",
                "acq_grab_time_end": "[f]",
                "acq_adc_time": "[f]",
                "acq_signal_length": "[f]",
                "acq_inhibit_time": "[f]",
                "acq_status": "[f]",
                "acq_time_of_flight": "[f]",
                "acq_start_point": "[f]",
                "sample_id": "[t]",
            }

        self.static_additions = {
            }

        self.key_translations = {
                "lat": ("[f]", "object_lat"),
                "latitude": ("[f]", "object_lat"),
                "lon": ("[f]", "object_lon"),
                "long": ("[f]", "object_lon"),
                "longitude": ("[f]", "object_lon"),
                "feature_extractor": ("[t]", "process_feature_extractor"),
                "volume_imaged": ("[f]", "acq_volimage"),
                "max_esd_save_threshold": ("[f]", "acq_min_esd"),
                "min_esd_save_threshold": ("[f]", "acq_max_esd"),
                "area": ("[f]", "object_area"),
                "convexarea": ("[f]", "object_convexarea"),
                "convexperimeter": ("[f]", "object_convexperimeter"),
                "extent": ("[f]", "object_extent"),
                "equivdiameter": ("[f]", "object_equivdiameter"),
                "eccentricity": ("[f]", "object_eccentricity"),
                "convexperimeter": ("[f]", "object_convexperimeter"),
                "convexarea": ("[f]", "object_convexarea"),
                "boundingbox_ywidth": ("[f]", "object_boundingbox_ywidth"),
                "boundingbox_xwidth": ("[f]", "object_boundingbox_xwidth"),
                "biovolume": ("[f]", "object_biovolume"),
                "bflip": ("[f]", "object_bflip"),
                "b90": ("[f]", "object_b90"),
                "b180": ("[f]", "object_b180"),
                "area_over_perimetersquared": ("[f]", "object_area_over_perimetersquared"),
                "area_over_perimeter": ("[f]", "object_area_over_perimeter"),
                "area": ("[f]", "object_area"),
                "date": ("[f]", "object_date"),
                "time": ("[f]", "object_time"),
                "texture_uniformity": ("[f]", "object_texture_uniformity"),
                "texture_third_moment": ("[f]", "object_texture_third_moment"),
                "texture_smoothness": ("[f]", "object_texture_smoothness"),
                "texture_entropy": ("[f]", "object_texture_entropy"),
                "texture_average_gray_level": ("[f]", "object_texture_average_gray_level"),
                "texture_average_contrast": ("[f]", "object_texture_average_contrast"),
                "surfacearea": ("[f]", "object_surfacearea"),
                "summedsurfacearea": ("[f]", "object_summedsurfacearea"),
                "summedperimeter": ("[f]", "object_summedperimeter"),
                "summedminoraxislength": ("[f]", "object_summedminoraxislength"),
                "summedmajoraxislength": ("[f]", "object_summedmajoraxislength"),
                "summedconvexperimeter_over_perimeter": ("[f]", "object_summedconvexperimeter_over_perimeter"),
                "summedconvexperimeter": ("[f]", "object_summedconvexperimeter"),
                "summedconvexarea": ("[f]", "object_summedconvexarea"),
                "summedbiovolume": ("[f]", "object_summedbiovolume"),
                "summedarea": ("[f]", "object_summedarea"),
                "solidity": ("[f]", "object_solidity"),
                "shapehist_skewness_normeqd": ("[f]", "object_shapehist_skewness_normeqd"),
                "shapehist_median_normeqd": ("[f]", "object_shapehist_median_normeqd"),
                "shapehist_mean_normeqd": ("[f]", "object_shapehist_mean_normeqd"),
                "shapehist_kurtosis_normeqd": ("[f]", "object_shapehist_kurtosis_normeqd"),
                "rwhalfpowerintegral": ("[f]", "object_rwhalfpowerintegral"),
                "rwcenter2total_powerratio": ("[f]", "object_rwcenter2total_powerratio"),
                "rotatedboundingbox_ywidth": ("[f]", "object_rotatedboundingbox_ywidth"),
                "rotatedboundingbox_xwidth": ("[f]", "object_rotatedboundingbox_xwidth"),
                "rotated_boundingbox_solidity": ("[f]", "object_rotated_boundingbox_solidity"),
                "roi_number": ("[f]", "object_roi_number"),
                "representativewidth": ("[f]", "object_representativewidth"),
                "perimeter": ("[f]", "object_perimeter"),
                "orientation": ("[f]", "object_orientation"),
                "numblobs": ("[f]", "object_numblobs"),
                "minoraxislength": ("[f]", "object_minoraxislength"),
                "minferetdiameter": ("[f]", "object_minferetdiameter"),
                "maxferetdiameter": ("[f]", "object_maxferetdiameter"),
                "majoraxislength": ("[f]", "object_majoraxislength"),
                "hflip_over_h180": ("[f]", "object_hflip_over_h180"),
                "hflip": ("[f]", "object_hflip"),
                "h90_over_hflip": ("[f]", "object_h90_over_hflip"),
                "h90_over_h180": ("[f]", "object_h90_over_h180"),
                "h90": ("[f]", "object_h90"),
                "h180": ("[f]", "object_h180"),
            }

        #,
        #        "": ("[]", "")

        if "ship_name" in self.options.keys():
            self.static_additions["sample_ship"] = self.options["ship_name"]
            self.ecotaxa_table_header["sample_ship"] = "[t]"
        if "cruise_name" in self.options.keys():
            self.static_additions["sample_cruise"] = self.options["cruise_name"]
            self.ecotaxa_table_header["sample_cruise"] = "[t]"
        if "project_name" in self.options.keys():
            self.static_additions["sample_project"] = self.options["project_name"]
            self.ecotaxa_table_header["sample_project"] = "[t]"


        if "station_id" in self.options.keys():
            self.static_additions["sample_stationid"] = self.options["station_id"]
            self.ecotaxa_table_header["sample_stationid"] = "[t]"
        if "ctd_cast" in self.options.keys():
            self.static_additions["sample_ctdcast"] = self.options["ctd_cast"]
            self.ecotaxa_table_header["sample_ctdcast"] = "[t]"
        if "sample_barcode" in self.options.keys():
            self.static_additions["sample_barcode"] = self.options["sample_barcode"]
            self.ecotaxa_table_header["sample_barcode"] = "[t]"
        if "sample_comment" in self.options.keys():
            self.static_additions["sample_comment"] = self.options["sample_comment"]
            self.ecotaxa_table_header["sample_comment"] = "[t]"
        if "sampling_gear" in self.options.keys():
            self.static_additions["sample_samplinggear"] = self.options["sampling_gear"]
            self.ecotaxa_table_header["sample_samplinggear"] = "[t]"
        if "initial_collected_volume_m3" in self.options.keys():
            self.static_additions["sample_initial_col_vol_m3"] = self.options["initial_collected_volume_m3"]
            self.ecotaxa_table_header["sample_initial_col_vol_m3"] = "[f]"
        if "concentrated_sample_volume_m3" in self.options.keys():
            self.static_additions["sample_concentrated_sample_volume"] = self.options["concentrated_sample_volume_m3"]
            self.ecotaxa_table_header["sample_concentrated_sample_volume"] = "[f]"
        if "dilution_factor" in self.options.keys():
            self.static_additions["sample_dilution_factor"] = self.options["dilution_factor"]
            self.ecotaxa_table_header["sample_dilution_factor"] = "[f]"
        if "operator_name" in self.options.keys():
            self.static_additions["sample_operator"] = self.options["operator_name"]
            self.ecotaxa_table_header["sample_operator"] = "[t]"
        if "dilution_method" in self.options.keys():
            self.static_additions["sample_dilution_method"] = self.options["dilution_method"]
            self.ecotaxa_table_header["sample_dilution_method"] = "[t]"
        if "fixative" in self.options.keys():
            self.static_additions["sample_fixative"] = self.options["fixative"]
            self.ecotaxa_table_header["sample_fixative"] = "[t]"
        if "sieve_min_um" in self.options.keys():
            self.static_additions["sample_sieve_min_um"] = self.options["sieve_min_um"]
            self.ecotaxa_table_header["sample_sieve_min_um"] = "[f]"
        if "sieve_max_um" in self.options.keys():
            self.static_additions["sample_sieve_max_um"] = self.options["sieve_max_um"]
            self.ecotaxa_table_header["sample_sieve_max_um"] = "[f]"
        if "feature_extractor_min_thresh" in self.options.keys():
            self.static_additions["process_min_thresh"] = self.options["feature_extractor_min_thresh"]
            self.ecotaxa_table_header["process_min_thresh"] = "[f]"
        if "feature_extractor_max_thresh" in self.options.keys():
            self.static_additions["process_max_thresh"] = self.options["feature_extractor_max_thresh"]
            self.ecotaxa_table_header["process_max_thresh"] = "[f]"
        if "um_per_pixel" in self.options.keys():
            self.static_additions["process_pixel_um"] = self.options["um_per_pixel"]
            self.ecotaxa_table_header["process_pixel_um"] = "[f]"


        if self.with_images:
            self.job_object.log_function("Creating EcoTaxa table for use alongside an image upload")
            self.ecotaxa_table_header["img_file_name"] = "[t]"
            self.ecotaxa_table_header["img_rank"] = "[f]"
        else:
            self.job_object.log_function("Creating EcoTaxa table only, without images")

        self.total_rois = 0
        for roi_reader in roi_readers:
            self.total_rois += len(roi_reader.rows)


    def add_csv_file(self, csv_fd, csv_filename):
        metadata_dict = list(csv.DictReader(csv_fd))
        dict_keys = metadata_dict[0].keys()
        can_join_dict = False
        metadata_dict_info = {
                "data_keys": [],
                "filename": csv_filename
            }
        bin_id_regex = re.compile(r'D[0-9]{8}T[0-9]{6}_IFCB[0-9]+')
        if ("bin" in dict_keys) or ("filename" in dict_keys):
            can_join_dict = True
            metadata_dict_info["bin_key_column"] = "filename"
            if "bin" in dict_keys:
                metadata_dict_info["bin_key_column"] = "bin"
        if ("roi_number" in dict_keys):
            can_join_dict = True
            metadata_dict_info["roi_key_column"] = "roi_number"
            result = bin_id_regex.search(csv_filename)
            metadata_dict_info["bin_match"] = result.group()
            metadata_dict_info["roi_key_index"] = {}
            for row_index in range(len(metadata_dict)):
                metadata_dict_info["roi_key_index"][int(metadata_dict[row_index][metadata_dict_info["roi_key_column"]])] = row_index
        if can_join_dict:
            metadata_dict_info["dict"] = metadata_dict
            matched_ecotaxa_columns = []
            matched_ecotaxa_types = []
            match_data_keys = []

            for candidate_key in self.key_translations.keys():
                if candidate_key in dict_keys:
                    match_data_keys.append(candidate_key)
                    matched_ecotaxa_types.append(self.key_translations[candidate_key][0])
                    matched_ecotaxa_columns.append(self.key_translations[candidate_key][1])

            for column_index in range(len(matched_ecotaxa_columns)):
                if matched_ecotaxa_columns[column_index] not in self.column_sources.keys():
                    self.column_sources[matched_ecotaxa_columns[column_index]] = []
                self.ecotaxa_table_header[matched_ecotaxa_columns[column_index]] = matched_ecotaxa_types[column_index]
                self.match_data_keys[matched_ecotaxa_columns[column_index]] = match_data_keys[column_index]
                self.column_sources[matched_ecotaxa_columns[column_index]].append(metadata_dict_info)

            self.job_object.log_function("Loading metadata file \"" + csv_filename + "\" with " + str(len(metadata_dict_info["dict"])) + " rows")

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.roi_readers[self.reader_index].rois):
            roi = self.roi_readers[self.reader_index].rois[self.index]
            dt = datetime.strptime(self.ifcb_ids[self.reader_index].split("_")[0], "D%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            observation_id = self.ifcb_ids[self.reader_index] + "_" + str(roi.index).zfill(5)
            ifcb_bin = self.ifcb_ids[self.reader_index]
            trigger_values = {}
            for key in roi.trigger.raw.keys():
                trigger_values[key] = float(roi.trigger.raw[key])
            trigger_id = self.ifcb_ids[self.reader_index] + "_TN" + str(int(trigger_values["trigger_number"]))
            ifcb_sn = self.ifcb_ids[self.reader_index].split("_")[1][4:]
            extents = [(0, roi.array.shape[0]), (0, roi.array.shape[1])]
            origin_extents = roi.array.shape

            record = {
                "object_id": observation_id,
                "object_date": dt.strftime("%Y-%m-%d"),
                "object_time":  dt.strftime("%H:%M:%S"),
                "object_roi_width": int(trigger_values["roi_width"]),
                "object_roi_height": int(trigger_values["roi_height"]),
                "process_id": None,
                "process_date": self.process_time.strftime("%Y-%m-%d"),
                "process_time": self.process_time.strftime("%H:%M:%S"),
                "acq_id": trigger_id,
                "acq_instrument": "IFCB",
                "acq_sn": ifcb_sn,
                "acq_operator": self.options["operator_name"],
                "acq_run_time": trigger_values["run_time"],
                "acq_trigger_number": trigger_values["trigger_number"],
                "acq_peak_b": trigger_values["peak_b"],
                "acq_pmt_b": trigger_values["pmt_b"],
                "acq_peak_a": trigger_values["peak_a"],
                "acq_pmt_a": trigger_values["pmt_a"],
                "acq_grab_time_end": trigger_values["grab_time_end"],
                "acq_grab_time_start": trigger_values["grab_time_start"],
                "acq_adc_time": trigger_values["adc_time"],
                "acq_signal_length": trigger_values["signal_length"],
                "acq_inhibit_time": trigger_values["inhibit_time"],
                "acq_status": trigger_values["status"],
                "acq_time_of_flight": trigger_values["time_of_flight"],
                "acq_start_point": trigger_values["start_point"],
                "sample_id": ifcb_bin,
            }

            # Add in denormalised data for the whole sample
            for key in self.static_additions.keys():
                record[key] = self.static_additions[key]

            # Add in data from CSV tables
            for ecotaxa_column in self.column_sources.keys():
                value = None
                for column_source in self.column_sources[ecotaxa_column]:
                    candidate = True
                    if "bin_match" in column_source.keys():
                        if not ifcb_bin == column_source["bin_match"]:
                            candidate = False
                    if candidate:
                        if "roi_key_column" in column_source.keys():
                            #for row in column_source["dict"]:
                            #    if int(row[column_source["roi_key_column"]]) == roi.index:
                            #        value = row[self.match_data_keys[ecotaxa_column]]
                            try:
                                row_index = column_source["roi_key_index"][roi.index]
                                value = column_source["dict"][row_index][self.match_data_keys[ecotaxa_column]]
                            except KeyError:
                                self.job_object.error_function("KeyError on matching ROI " + str(roi.index) + " from bin \"" + self.ifcb_ids[self.reader_index] + "\" to row in CSV \"" + column_source["filename"] + "\" for column \"" + ecotaxa_column + "\"")
                        if "bin_key_column" in column_source.keys():
                            for row in column_source["dict"]:
                                if row[column_source["bin_key_column"]] == ifcb_bin:
                                    value = row[self.match_data_keys[ecotaxa_column]]
                if value is None:
                    self.job_object.error_function("MISSING SOME DATA FOR " + observation_id)
                else:
                    record[ecotaxa_column] = value

            # Only advance indexes at the end!
            self.index += 1
            if self.index >= len(self.roi_readers[self.reader_index].rois):
                if self.reader_index < (len(self.roi_readers) - 1):
                    self.reader_index += 1
                    self.index = 0

            if self.with_images:
                record["img_file_name"] = observation_id + ".png"
                record["img_rank"] = 0
                return (record, roi.image)
            else:
                return (record, )
        raise StopIteration

class MainJob:
    def calc_progress_report(self):
        self.last_time = time.time()
        proportion = self.currently_processing/self.total_rois
        elapsed_time = self.last_time - self.first_time
        time_per_roi = elapsed_time / self.currently_processing
        remaining_rois = self.total_rois - self.currently_processing
        remaining_time = time_per_roi * remaining_rois
        self.report_progress(proportion, remaining_time)

    def __init__(self, options, progress_reporting_function = lambda prop, etr : print(str(int(prop*10000)/100) + "% done - ETR " + str(int(etr)) + "s"), log_function = lambda txt : print("[LOG] " + txt), error_function = lambda txt : print("[ERR] " + txt)):

        self.options = options
        self.report_progress = progress_reporting_function
        self.log_function = log_function
        self.error_function = error_function

        #print(options)

        if "table_only" in options.keys():
            self.with_images = not options["table_only"]
        else:
            self.with_images = True

        input_files_list = []
        for input_file_path in options["input_files"]:
            input_files_list.append(os.path.realpath(input_file_path))

        #print(input_files_list)

        ifcb_bins = []
        ifcb_files = []
        roi_readers = []

        intermediate_files_list = set()
        csv_files_list = set()
        for file_name in input_files_list:
            splitext = os.path.splitext(file_name)
            if (splitext[1] == ".hdr") or (splitext[1] == ".adc") or (splitext[1] == ".roi"):
                intermediate_files_list.add(splitext[0])
            elif (splitext[1] == ".csv"):
                csv_files_list.add(file_name)

        for file_name in intermediate_files_list:
            ifcb_bins.append(os.path.basename(file_name))
            ifcb_files.append(file_name)

        if len(ifcb_bins) == 0:
            raise RuntimeException("No IFCB bins supplied!")

        self.log_function("Creating ROIReaders")

        for i in range(len(ifcb_files)):
            self.log_function("Loading \"" + ifcb_files[i] + ".hdr\"")
            roi_readers.append(libifcb.ROIReader(ifcb_files[i] + ".hdr", ifcb_files[i] + ".adc", ifcb_files[i] + ".roi"))

        self.log_function("Initialising entry provider")
        self.entry_provider = IFCBEntryProvider(roi_readers, ifcb_bins, self, self.with_images, options)

        for csv_file in csv_files_list:
            self.entry_provider.add_csv_file(open(csv_file, "r"), csv_file)

        self.total_rois = self.entry_provider.total_rois

    def execute(self):
        self.first_time = time.time()
        self.currently_processing = 0
        self.last_time = time.time()

        if self.with_images:
            zip_files = 1
            out_zip = None
            max_size = None
            out_file = self.options["output_file"]
            out_file_se = os.path.splitext(out_file)
            if max_size is not None:
                out_zip = zipfile.ZipFile(out_file_se[0] + "_part" + str(zip_files) + out_file_se[1], 'w')
            else:
                out_zip = zipfile.ZipFile(out_file, 'w')

            container = os.path.basename(out_file_se[0]) + "_part" + str(zip_files)

            ecotaxa_md = io.StringIO()
            ecotaxa_md_writer = csv.DictWriter(ecotaxa_md, fieldnames=self.entry_provider.ecotaxa_table_header.keys(), quoting=csv.QUOTE_NONNUMERIC, delimiter='\t', lineterminator='\n')
            ecotaxa_md_writer.writeheader()
            ecotaxa_md_writer.writerow(self.entry_provider.ecotaxa_table_header)
            running_compressed_size = 0
            tsv_name_suffix = ""

            try:
                while True:
                    entry = next(self.entry_provider)
                    self.currently_processing += 1
                    tsv_name_suffix = entry[0]["sample_id"] # So every TSV is likely to have a different, but predictable name
                    ecotaxa_md_writer.writerow(entry[0])

                    imbuffer = io.BytesIO()
                    entry[1].save(imbuffer, "png")
                    imbytes = imbuffer.getvalue()
                    running_compressed_size += len(imbytes)
                    out_zip.writestr(container + "/" + entry[0]["img_file_name"], imbytes)

                    if (self.currently_processing % 512) == 0:
                        self.calc_progress_report()

                    if max_size is not None:
                        if running_compressed_size > max_size:
                            zip_files += 1
                            out_zip.writestr(container + "/ecotaxa_" + tsv_name_suffix + ".tsv", ecotaxa_md.getvalue())
                            out_zip.close()
                            out_zip = zipfile.ZipFile(out_file_se[0] + "_part" + str(zip_files) + out_file_se[1], 'w')
                            container = os.path.basename(out_file_se[0]) + "_part" + str(zip_files)
                            ecotaxa_md = io.StringIO()
                            ecotaxa_md_writer = csv.DictWriter(ecotaxa_md, fieldnames=self.entry_provider.ecotaxa_table_header.keys(), quoting=csv.QUOTE_NONNUMERIC, delimiter='\t', lineterminator='\n')
                            ecotaxa_md_writer.writeheader()
                            ecotaxa_md_writer.writerow(self.entry_provider.ecotaxa_table_header)
                            running_compressed_size = 0
            except StopIteration:
                pass

            out_zip.writestr(container + "/ecotaxa_" + tsv_name_suffix + ".tsv", ecotaxa_md.getvalue())
            out_zip.close()
        else:
            with open(self.options["output_file"], "w") as ecotaxa_md:
                ecotaxa_md_writer = csv.DictWriter(ecotaxa_md, fieldnames=self.entry_provider.ecotaxa_table_header.keys(), quoting=csv.QUOTE_NONNUMERIC, delimiter='\t', lineterminator='\n')
                ecotaxa_md_writer.writeheader()
                ecotaxa_md_writer.writerow(self.entry_provider.ecotaxa_table_header)

                try:
                    while True:
                        entry = next(self.entry_provider)
                        self.currently_processing += 1
                        ecotaxa_md_writer.writerow(entry[0])
                        if (self.currently_processing % 512) == 0:
                            self.calc_progress_report()
                except StopIteration:
                    pass



