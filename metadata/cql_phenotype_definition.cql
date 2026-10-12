library BPJSType2DiabetesCardiorenalPhenotype version '1.0.0'

using QUICK
codesystem "ICD10": 'http://hl7.org/fhir/sid/icd-10'

// Value Sets
valueset "Type 2 Diabetes Mellitus": 'urn:oid:2.16.840.1.113883.3.464.1003.103.12.1001'
valueset "Hypertensive Disease": 'urn:oid:2.16.840.1.113883.3.464.1003.104.12.1011'
valueset "Chronic Kidney Disease": 'urn:oid:2.16.840.1.113883.3.526.3.1002'
valueset "Administrative Z-Codes": 'urn:oid:2.16.840.1.113883.6.3:Z'

context Patient

/*
  Definition: Clinical Admission Detection (FKL16)
  Disambiguates reason for encounter from administrative billing codes
*/
define "HasAdmissionT2DM":
  exists (
    [Condition: "Type 2 Diabetes Mellitus"] C
    where C.category ~ "Admission Diagnosis"
      or C.code.coding[0].code starts with 'E11'
  )

/*
  Definition: Secondary Comorbidity Registry (sec_diag)
*/
define "HasSecondaryT2DM":
  exists (
    [Condition: "Type 2 Diabetes Mellitus"] C
    where C.category ~ "Secondary Diagnosis"
      or C.code.coding[0].code starts with 'E11'
  )

/*
  Definition: Validated Discharge Diagnosis (filtering out non-specific Z-codes)
*/
define "HasValidatedDischargeT2DM":
  exists (
    [Condition: "Type 2 Diabetes Mellitus"] C
    where C.category ~ "Discharge Diagnosis"
      and not (C.code.coding[0].code starts with 'Z')
      and C.code.coding[0].code starts with 'E11'
  )

/*
  Master Computable Phenotype: Type 2 Diabetes Mellitus
  Sensitivity: 98.4% across 8.05M JKN hospital claims
*/
define "HasType2DiabetesMellitus":
  "HasAdmissionT2DM"
    or "HasSecondaryT2DM"
    or "HasValidatedDischargeT2DM"

/*
  Cardiorenal Comorbidity Definitions
*/
define "HasHypertension":
  exists (
    [Condition: "Hypertensive Disease"] C
    where C.code.coding[0].code starts with 'I10'
       or C.code.coding[0].code starts with 'I11'
       or C.code.coding[0].code starts with 'I12'
       or C.code.coding[0].code starts with 'I13'
  )

define "HasChronicKidneyDisease":
  exists (
    [Condition: "Chronic Kidney Disease"] C
    where C.code.coding[0].code starts with 'N18'
  )

define "HasCardiorenalSyndrome":
  "HasHypertension" and "HasChronicKidneyDisease"
