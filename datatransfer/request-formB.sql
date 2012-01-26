DROP TABLE IF EXISTS `cc_export_tmp`;

CREATE TEMPORARY TABLE `cc_export_tmp`
SELECT 'id' as id, 'delta_days', 'encounter_date', 'encounter_year', 'encounter_month', 
'encounter_day', 'encounter_type', 'chw', 'hohh', 'location', 'counseling_codes', 
'available', 'numofchildren', 'noofwomen', 'womenusingfp',
  'numofsick', 'numofrdtusedonother', 'numofrdtpositive', 'numontreatement'
 UNION;
SELECT
  cc_ccrpt.encounter_id as id,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  (SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ) as encounter_date,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  v_cc_hhvisitrpt_counseling.codes as counseling_codes,
  cc_hhvisitrpt.available as available,
  cc_hhvisitrpt.children as numofchildren,
  NULL as noofwomen, NULL as womenusingfp,
  NULL          AS numofsick,
  NULL          AS numofrdtusedonother,
  NULL AS numofrdtpositive,
  NULL  AS numontreatement
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
  (SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ) as encounter_date,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  NULL as counseling_codes, NULL as available, NULL as numofchildren,
  cc_fprpt.women as noofwomen,
  cc_fprpt.women_using as womenusingfp,
  NULL          AS numofsick,
  NULL          AS numofrdtusedonother,
  NULL AS numofrdtpositive,
  NULL  AS numontreatement
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
  (SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ) as encounter_date,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as hohh_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  NULL as counseling_codes, NULL as available, NULL as numofchildren,
  NULL as noofwomen,
  NULL as womenusingfp,
  cc_sickrpt.sick          AS numofsick,
  cc_sickrpt.rdts          AS numofrdtusedonother,
  cc_sickrpt.positive_rdts AS numofrdtpositive,
  cc_sickrpt.on_treatment  AS numontreatement
FROM
  cc_ccrpt
INNER JOIN cc_sickrpt
ON
  cc_sickrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
  ;
  
ALTER TABLE cc_export_tmp DROP delta_days;

SELECT * 
INTO OUTFILE '/tmp/formB.csv' 
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
  LINES TERMINATED BY '\n'
FROM cc_export_tmp;

DROP TABLE IF EXISTS `cc_export_tmp`;
