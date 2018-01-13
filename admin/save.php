<?php 
if(isset($_POST['lists']) 
&& isset($_POST['ballots']) 
&& isset($_POST['votes']) 
&& isset($_POST['colours']) 
&& isset($_POST['meta']) 
&& isset($_POST['timestamp'])){
	$success = file_put_contents("../data/data.json", json_encode($_POST,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
	$success &= file_put_contents("../data/timestamp.json", json_encode(array('last_update' => $_POST['timestamp'])));
	if($success === false){
		echo '{"status":"write_error"}';
	} else {
		echo '{"status":"ok"}';
	}
} else {
	echo '{"status":"post_data_error"}';
}
?>