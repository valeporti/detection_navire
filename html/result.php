<?php 
$conn = new mysqli("localhost", "ps4", "ps4","ps4");
?>

<!DOCTYPE html>
<html lang="en">
<head>
	<title>Interface plateforme</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
<!--===============================================================================================-->	
	<link rel="icon" type="image/png" href="images/icons/favicon.ico"/>
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="vendor/bootstrap/css/bootstrap.min.css">
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="fonts/font-awesome-4.7.0/css/font-awesome.min.css">
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="vendor/animate/animate.css">
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="vendor/select2/select2.min.css">
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="vendor/perfect-scrollbar/perfect-scrollbar.css">
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="css/util.css">
	<link rel="stylesheet" type="text/css" href="css/main.css">
<!--===============================================================================================-->
</head>
<body>
	<div class="limiter">
		<div class="container-table100">
			<div class="wrap-table100">
				<div class="table100 ver4 m-b-110">
					<div class="table100-head">
						<table>
							<thead>
								<tr class="row100 head">
									<th class="cell100 column1">Type</th>
									<th class="cell100 column2">Date</th>
									<th class="cell100 column3">Nombre de détections</th>
									<th class="cell100 column4">Référence</th>
								</tr>
							</thead>
						</table>
					</div>



<?php if(isset($_GET["startDay"]) & isset($_GET["endDay"]) & isset($_GET["geojson"])) {
$sql = "SELECT * FROM Localisation;";
$result = $conn->query($sql);

$searchSql = "SELECT * FROM Image WHERE date BETWEEN '" . $_GET["startDay"] . "' AND '" . $_GET["endDay"]."'";

if(isset($_GET["S1"]) & !isset($_GET["S2"])) $searchSql = $searchSql . " AND type=S1 ";
if(!isset($_GET["S1"]) & isset($_GET["S2"])) $searchSql = $searchSql . " AND type=S2 ";

$toExportImageIds = array();

$searchSql = $searchSql . " AND localisation='".$_GET["geojson"]."';";
$result = $conn->query($searchSql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
	$ref = $row["ImId"];
        array_push($toExportImageIds,$row["id"]);
	if(strlen($ref)>20){
	    $stringCut = substr($ref, 0, 20);
    		$endPoint = strrpos($stringCut, ' ');
		$string = $endPoint? substr($stringCut, 0, $endPoint) : substr($stringCut, 0);
		$string .= '...';
		$ref = $string;
	}
$detectionPath = 'http://'.$_SERVER["HTTP_HOST"].'/'.$row["ImId"];
	echo "

<div class='table100-body js-pscroll'>
	<table>
		<tbody>
			<tr class='row100 body'>
				<td class='cell100 column1'>".$row["type"]."</td>
				<td class='cell100 column2'>".$row["date"]."</td>
				<td class='cell100 column3'><a href=".$detectionPath." target='_blank'>".$row["nr_detections"]."</a></td>
				<td class='cell100 column4'>".$ref."</td>
			</tr>
			</tr>
		</tbody>
	</table>
</div>";

    }}
}
?>

<br><br><center>
<form action="./resultat_recherche.kml">
<input type="submit" value="Télécharger KML">
</form>
</center>
				</div>
			</div>
		</div>
	</div>


<!--===============================================================================================-->	
	<script src="vendor/jquery/jquery-3.2.1.min.js"></script>
<!--===============================================================================================-->
	<script src="vendor/bootstrap/js/popper.js"></script>
	<script src="vendor/bootstrap/js/bootstrap.min.js"></script>
<!--===============================================================================================-->
	<script src="vendor/select2/select2.min.js"></script>
<!--===============================================================================================-->
	<script src="vendor/perfect-scrollbar/perfect-scrollbar.min.js"></script>
	<script>
		$('.js-pscroll').each(function(){
			var ps = new PerfectScrollbar(this);

			$(window).on('resize', function(){
				ps.update();
			})
		});
			
		
	</script>
<!--===============================================================================================-->
	<script src="js/main.js"></script>

</body>
</html>

<?php
// Creates an array of strings to hold the lines of the KML file.
file_put_contents("resultat_recherche.kml","");
$kmlfile = fopen("resultat_recherche.kml","w");
$kml = array('<?xml version="1.0" encoding="UTF-8"?>');
$kml[] = '<kml xmlns="http://earth.google.com/kml/2.1">';
$kml[] = ' <Document>';
$kml[] = ' <Style id="restaurantStyle">';
$kml[] = ' <IconStyle id="restuarantIcon">';
$kml[] = ' <Icon>';
$kml[] = ' <href>http://maps.google.com/mapfiles/kml/pal2/icon63.png</href>';
$kml[] = ' </Icon>';
$kml[] = ' </IconStyle>';
$kml[] = ' </Style>';
$kml[] = ' <Style id="barStyle">';
$kml[] = ' <IconStyle id="barIcon">';
$kml[] = ' <Icon>';
$kml[] = ' <href>http://maps.google.com/mapfiles/kml/pal2/icon27.png</href>';
$kml[] = ' </Icon>';
$kml[] = ' </IconStyle>';
$kml[] = ' </Style>';

foreach ($toExportImageIds as $imageId) {
// Iterates through the rows, printing a node for each row.
$searchSql = "SELECT * FROM Detection,Image WHERE Detection.ImId = Image.ImId AND Image.id = ". $imageId . ";";
$result = $conn->query($searchSql);
while($row = $result->fetch_assoc()) 
{
  $imagePath = 'http://'.$_SERVER["HTTP_HOST"].'/'.$row["ImId"].'/'. $row["target_number"]. '.jpg';
  $kml[] = ' <Placemark id="placemark' . $row['ImId'] . '">';
  $kml[] = ' <name>'.$row['date'].':i' . htmlentities($row['id']) . "_n" . $row["target_number"] . '</name>';
  $kml[] = ' <description><center><div style="height:100px;width:100px;"><img style="height: 100%; width: 100%; object-fit: contain" src="'.$imagePath.'"/></div><a href="'.$imagePath.'" target="_blank">Agrandir</a><br/>Latitude : '  . $row['lat'] . '<br/>Longitude : '  . $row['lon'] . '<br/>Date : '.$row['date'].'<br/>Nom image : '.$row['ImId'].'<br/>Numéro détection sur l\'image : '.$row['target_number'].'</center></description>';
  $kml[] = ' <Point>';
  $kml[] = ' <coordinates>' . $row['lon'] . ','  . $row['lat'] . '</coordinates>';
  $kml[] = ' </Point>';
  $kml[] = ' </Placemark>';
 
}}

// End XML file
$kml[] = ' </Document>';
$kml[] = '</kml>';
$kmlOutput = join("\n", $kml);
fwrite($kmlfile,$kmlOutput);
fclose($kmlfile);

$conn->close();
?>

