DROP TABLE IF EXISTS `cc_export_tmp`;

CREATE TEMPORARY TABLE `cc_export_tmp`
SELECT 'Seq' as Seq, 'delta_days', 'encounter_date', 'encounter_date_mod', 'encounter_year_mod', 'encounter_month_mod', 
'encounter_day_mod', 'encounter_type', 'chw', 'hohh', 'location', 'V1_available',  'V2_numofchildren', 'V3_counseling_codes',
  'E1_numofsick', 'E2_numofrdtusedonother', 'E3_numofrdtpositive', 'E4_numontreatement', 
 'P1_noofwomen', 'P2_womenusingfp', 'P3_num_pills_given', 'P4_num_women_given_pills', 'source'
 UNION
SELECT
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  cc_hhvisitrpt.available as available,
  cc_hhvisitrpt.children as numofchildren,
  v_cc_hhvisitrpt_counseling.codes as counseling_codes,
  NULL          AS numofsick,
  NULL          AS numofrdtusedonother,
  NULL AS numofrdtpositive,
  NULL  AS numontreatement,
  NULL as noofwomen, NULL as womenusingfp,
  NULL AS num_pills_given,
  NULL AS num_women_given_pills,
  CASE WHEN EXTRACT(HOUR FROM cc_encounter.encounter_date)=12 AND EXTRACT(MINUTE FROM cc_encounter.encounter_date)=0 AND EXTRACT(SECOND FROM cc_encounter.encounter_date)=0 THEN 'D' ELSE 'S' END AS source
FROM
  cc_hhvisitrpt
INNER JOIN cc_ccrpt
ON
  cc_hhvisitrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
INNER JOIN
  (
    SELECT
      m.householdvisitreport_id,
      Group_Concat(m.code) AS codes
    FROM
      (
        SELECT
          cc_hhvisitrpt_counseling.householdvisitreport_id,
          cc_codeditem.code,
          cc_codeditem.type
        FROM
          cc_hhvisitrpt_counseling
        INNER JOIN cc_codeditem
        ON
          cc_hhvisitrpt_counseling.codeditem_id = cc_codeditem.id
        ORDER BY
          cc_hhvisitrpt_counseling.householdvisitreport_id
      ) AS m
    GROUP BY
      m.householdvisitreport_id
  )
  v_cc_hhvisitrpt_counseling ON cc_hhvisitrpt.ccreport_ptr_id =
  v_cc_hhvisitrpt_counseling.householdvisitreport_id
UNION
  SELECT
  cc_ccrpt.encounter_id as id,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
 NULL as available, NULL as numofchildren,  NULL as counseling_codes,
  NULL          AS numofsick,
  NULL          AS numofrdtusedonother,
  NULL AS numofrdtpositive,
  NULL  AS numontreatement,
  cc_fprpt.women as noofwomen,
  cc_fprpt.women_using as womenusingfp,
  NULL AS num_pills_given,
  NULL AS num_women_given_pills,
  CASE WHEN EXTRACT(HOUR FROM cc_encounter.encounter_date)=12 AND EXTRACT(MINUTE FROM cc_encounter.encounter_date)=0 AND EXTRACT(SECOND FROM cc_encounter.encounter_date)=0 THEN 'D' ELSE 'S' END AS source
FROM
  cc_ccrpt
INNER JOIN cc_fprpt
ON
  cc_fprpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
SELECT
  cc_ccrpt.encounter_id as id,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
 NULL as available, NULL as numofchildren,  NULL as counseling_codes,
  cc_sickrpt.sick          AS numofsick,
  cc_sickrpt.rdts          AS numofrdtusedonother,
  cc_sickrpt.positive_rdts AS numofrdtpositive,
  cc_sickrpt.on_treatment  AS numontreatement,
  NULL as noofwomen,
  NULL as womenusingfp,
  NULL AS num_pills_given,
  NULL AS num_women_given_pills,
  CASE WHEN EXTRACT(HOUR FROM cc_encounter.encounter_date)=12 AND EXTRACT(MINUTE FROM cc_encounter.encounter_date)=0 AND EXTRACT(SECOND FROM cc_encounter.encounter_date)=0 THEN 'D' ELSE 'S' END AS source
FROM
  cc_ccrpt
INNER JOIN cc_sickrpt
ON
  cc_sickrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
SELECT
  cc_ccrpt.encounter_id as id,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  NULL as available, NULL as numofchildren, NULL as counseling_codes,
  NULL          AS numofsick,
  NULL          AS numofrdtusedonother,
  NULL AS numofrdtpositive,
  NULL  AS numontreatement,
  NULL as noofwomen,
  NULL as womenusingfp,
  cc_bcprpt.pills AS num_pills_given,
  cc_bcprpt.women AS num_women_given_pills,
  CASE WHEN EXTRACT(HOUR FROM cc_encounter.encounter_date)=12 AND EXTRACT(MINUTE FROM cc_encounter.encounter_date)=0 AND EXTRACT(SECOND FROM cc_encounter.encounter_date)=0 THEN 'D' ELSE 'S' END AS source
FROM  cc_ccrpt
INNER JOIN cc_bcprpt
ON
  cc_bcprpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
  ;

ALTER TABLE cc_export_tmp DROP Seq;
ALTER TABLE cc_export_tmp DROP delta_days;
ALTER TABLE cc_export_tmp DROP encounter_date;
ALTER TABLE cc_export_tmp DROP encounter_year_mod;
ALTER TABLE cc_export_tmp DROP encounter_month_mod;
ALTER TABLE cc_export_tmp DROP encounter_day_mod;
DELETE FROM cc_export_tmp WHERE encounter_date_mod >= DATE_SUB(NOW(), INTERVAL 30 DAY);

set @oFilename = "";
PREPARE stmt1 FROM 'SELECT CONCAT("/tmp/", substring(research_id, 1,2), "_Form_B_", DATE_FORMAT(NOW(), "%Y-%m-%d"), ".csv") INTO @oFilename  FROM research_patient limit 1';
EXECUTE stmt1;
set @oOutput = CONCAT('SELECT * INTO OUTFILE "', @oFilename, '"  FIELDS TERMINATED BY "," OPTIONALLY ENCLOSED BY \'"\' LINES TERMINATED BY \'\n\' FROM cc_export_tmp');
PREPARE stmt2 FROM @oOutput;         
EXECUTE stmt2;
DEALLOCATE PREPARE stmt1;
DEALLOCATE PREPARE stmt2;

DROP TABLE IF EXISTS `cc_export_tmp`;
