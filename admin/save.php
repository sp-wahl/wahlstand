<?php 

if(isset($_POST['lists']) && isset($_POST['ballots']) && isset($_POST['votes'])){
	$success = file_put_contents("../data/data.json", json_encode($_POST,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
	if($success === false){
		echo '{"status":"write_error"}';
	} else {
		echo '{"status":"ok"}';
	}
} else {
	echo '{"status":"post_data_error"}';
}

?>