USE zillow;



select max(transactiondate), parcelid from predictions_2017 group by parcelid; 

SELECT e.*, properties_2017.buildingclasstypeid, buildingclasstype.buildingclassdesc
FROM (select max(transactiondate), parcelid from predictions_2017 group by parcelid) AS e
JOIN properties_2017 USING (parcelid)
LEFT JOIN airconditioningtype USING (airconditioningtypeid)
LEFT JOIN architecturalstyletype USING (architecturalstyletypeid)
LEFT JOIN buildingclasstype USING (buildingclasstypeid);

SELECT predictions_2017.logerror, e.transdate, 
		properties_2017.*, 
        typeconstructiontype.typeconstructiondesc, 
        storytype.storydesc, 
        propertylandusetype.propertylandusedesc, 
        heatingorsystemtype.heatingorsystemdesc, 
        airconditioningtype.airconditioningdesc, 
        architecturalstyletype.architecturalstyledesc, 
        buildingclasstype.buildingclassdesc
	FROM (SELECT max(transactiondate) AS transdate, parcelid FROM predictions_2017 GROUP BY parcelid) AS e
		JOIN predictions_2017 ON predictions_2017.transactiondate = e.transdate AND predictions_2017.parcelid = e.parcelid
        JOIN properties_2017 ON properties_2017.parcelid = predictions_2017.parcelid
		LEFT JOIN airconditioningtype USING (airconditioningtypeid)
		LEFT JOIN architecturalstyletype USING (architecturalstyletypeid)
		LEFT JOIN buildingclasstype USING (buildingclasstypeid)
		LEFT JOIN heatingorsystemtype USING (heatingorsystemtypeid)
		LEFT JOIN propertylandusetype USING (propertylandusetypeid)
		LEFT JOIN storytype USING (storytypeid)
		LEFT JOIN typeconstructiontype USING (typeconstructiontypeid);