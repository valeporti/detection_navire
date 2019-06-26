<?php 
$conn = new mysqli("localhost", "ps4", "ps4","ps4");
?>

<center>
<form action="/result.php" method="get">
  GeoJSON :<br>
 <select name="geojson">
<?php 
$sql = "SELECT * FROM Localisation;";
$result = $conn->query($sql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
	$geojson = $row["localisation"];
	echo "<option value='".$geojson."'>".$geojson."</option>";
    }} ?>
</select> 
<br><br>

  Plateforme Sentinel :<br>
<input type='checkbox' name='S1' checked> Sentinel 1 (SAR)<br>
<input type='checkbox' name='S2' checked> Sentinel 2 (MSI)<br>
<br><br>

  Date début :<br>
<input type="date" name="startDay">
<br><br>

  Date fin :<br>
<input type="date" name="endDay">
<br><br><br><br>

<input type="submit" value="Rechercher">

</form>
</center>
<?php $conn->close(); ?>
