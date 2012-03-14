DROP TABLE IF EXISTS `cc_export_tmp`;

CREATE TEMPORARY TABLE `cc_export_tmp`
SELECT 'Seq' as Seq, 'delta_days', 'encounter_date', 'encounter_date_mod', 'encounter_year_mod', 'encounter_month_mod', 
'encounter_day_mod', 'encounter_type', 'chw', 'hohh', 'patient_id', 'location', 'U1_visited_clinic',
'U2_improvement', 'S1_danger_signs', 'P1_month_of_pregnancy', 'P2_no_of_anc_visits',
  'P3_weeks_since_last_anc','N1_neonatal_clinic_visits', 'T1_breast_feeding_only', 'T2_immunized', 'M1_muac', 'M2_oedema',
  'M3_weight', 'nutrition_status', 'F1_rdt_result', 'G1_medicines_given', 'R1_referral'
 UNION
SELECT -- Followup Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  cc_furpt.visited_clinic AS visited_clinic,
  cc_furpt.improvement    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized  ,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_furpt
ON
  cc_furpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
SELECT -- Danger Signs Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  NULL AS visited_clinic,
  NULL    AS improvement,
  v_cc_danger_signs.codes as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_dsrpt
INNER JOIN cc_ccrpt
ON
  cc_dsrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
INNER JOIN
  (
    
  SELECT
      ds.dangersignsreport_id,
      Group_Concat(ds.code) AS codes
    FROM
      (
        SELECT
          cc_dsrpt_danger_signs.dangersignsreport_id,
          cc_codeditem.code,
          cc_codeditem.type
        FROM
          cc_dsrpt_danger_signs
        INNER JOIN cc_codeditem
        ON
          cc_dsrpt_danger_signs.codeditem_id = cc_codeditem.id
        ORDER BY
          cc_dsrpt_danger_signs.dangersignsreport_id
      ) AS ds
    GROUP BY
      ds.dangersignsreport_id
  )
 v_cc_danger_signs ON cc_dsrpt.ccreport_ptr_id =
  v_cc_danger_signs.dangersignsreport_id
UNION
SELECT -- Neonatal Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  cc_pregrpt.pregnancy_month AS month_of_pregnancy,
  cc_pregrpt.anc_visits      AS no_of_anc_visits,
  cc_pregrpt.weeks_since_anc AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized  ,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_pregrpt
ON
  cc_pregrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION  
  SELECT -- UnderOne Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  cc_neorpt.clinic_visits AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_neorpt
ON
  cc_neorpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
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
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  cc_uonerpt.breast_only AS breast_feeding_only,
  cc_uonerpt.immunized   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_uonerpt
ON
  cc_uonerpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
  SELECT -- Nutrition Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  cc_nutrpt.muac   AS muac,
  cc_nutrpt.oedema AS oedema,
  cc_nutrpt.weight AS weight,
  cc_nutrpt.status AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_nutrpt
ON
  cc_nutrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
  SELECT -- Fever Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  cc_fevrpt.rdt_result AS rdt_result,
  NULL as medicines_given,
  NULL AS referral
FROM
  cc_ccrpt
INNER JOIN cc_fevrpt
ON
  cc_fevrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
SELECT -- Referral Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location,
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  NULL as medicines_given,
  cc_refrpt.urgency AS referral
FROM
  cc_ccrpt
INNER JOIN cc_refrpt
ON
  cc_refrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
UNION
SELECT -- Medicine Given Report
  cc_ccrpt.encounter_id as Seq,
  (SELECT rp.days FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as delta_days,  # to remove
  DATE_FORMAT(cc_encounter.encounter_date, '%Y-%m-%d') as encounter_date, # to remove
  DATE_FORMAT((SELECT DATE_ADD(cc_encounter.encounter_date,  INTERVAL delta_days DAY) ), '%Y-%m-%d') as encounter_date_mod,
    (SELECT YEAR(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_year_mod,
      (SELECT MONTH(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_month_mod,
      (SELECT DAY(DATE_ADD(encounter_date,  INTERVAL delta_days DAY))) as encounter_day_mod,
  cc_encounter.type as encounter_type,
  (SELECT rchw.research_id FROM cc_patient as p, research_chw as rchw WHERE p.id=cc_encounter.patient_id AND rchw.chw_id=p.chw_id) as chw,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=(select cc_patient.household_id from cc_patient where cc_patient.id=cc_encounter.patient_id) AND p.health_id=rp.health_id) as hohh,
  (SELECT rp.research_id FROM cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id) as patient_id,
  (SELECT rl.research_id FROM research_location as rl, cc_patient as p, research_patient as rp WHERE p.id=cc_encounter.patient_id AND p.health_id=rp.health_id AND rl.location_id=p.location_id) as location, 
  NULL AS visited_clinic,
  NULL    AS improvement,
  NULL as danger_signs,
  NULL AS month_of_pregnancy,
  NULL      AS no_of_anc_visits,
  NULL AS weeks_since_last_anc,
  NULL AS neonatal_clinic_visits,
  NULL AS breast_feeding_only,
  NULL   AS immunized,
  NULL   AS muac,
  NULL AS oedema,
  NULL AS weight,
  NULL AS nutrition_status,
  NULL AS rdt_result,
  v_cc_medicines_given.codes as medicines_given,
  NULL AS referral
FROM
  cc_medsrpt
INNER JOIN cc_ccrpt
ON
  cc_medsrpt.ccreport_ptr_id = cc_ccrpt.id
INNER JOIN cc_encounter
ON
  cc_encounter.id = cc_ccrpt.encounter_id
INNER JOIN
  (
    
  SELECT
      med.medicinegivenreport_id,
      Group_Concat(med.code) AS codes
    FROM
      (
        SELECT
          cc_medsrpt_medicines.medicinegivenreport_id,
          cc_codeditem.code,
          cc_codeditem.type
        FROM
          cc_medsrpt_medicines
        INNER JOIN cc_codeditem
        ON
          cc_medsrpt_medicines.codeditem_id = cc_codeditem.id
        ORDER BY
          cc_medsrpt_medicines.medicinegivenreport_id
      ) AS med
    GROUP BY
      med.medicinegivenreport_id
  )
 v_cc_medicines_given ON cc_medsrpt.ccreport_ptr_id =
  v_cc_medicines_given.medicinegivenreport_id ;  
  
ALTER TABLE cc_export_tmp DROP delta_days;
ALTER TABLE cc_export_tmp DROP encounter_year_mod;
ALTER TABLE cc_export_tmp DROP encounter_month_mod;
ALTER TABLE cc_export_tmp DROP encounter_day_mod;
ALTER TABLE cc_export_tmp DROP nutrition_status;


set @oFilename = "";
PREPARE stmt1 FROM 'SELECT CONCAT("/tmp/", substring(research_id, 1,2), "_Form_C_", DATE_FORMAT(NOW(), "%Y-%m-%d"), ".csv") INTO @oFilename  FROM research_patient limit 1';
EXECUTE stmt1;
set @oOutput = CONCAT('SELECT * INTO OUTFILE "', @oFilename, '"  FIELDS TERMINATED BY "," OPTIONALLY ENCLOSED BY \'"\' LINES TERMINATED BY \'\n\' FROM cc_export_tmp');
PREPARE stmt2 FROM @oOutput;         
EXECUTE stmt2;
DEALLOCATE PREPARE stmt1;
DEALLOCATE PREPARE stmt2;

DROP TABLE IF EXISTS `cc_export_tmp`;
