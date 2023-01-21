<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    if(isset($data['lists'])
    && isset($data['ballots'])
    && isset($data['votes'])
    && isset($data['lastElectionVotes'])
    && isset($data['colours'])
    && isset($data['meta'])
    && isset($data['timestamp'])){
        $success = file_put_contents("../data/data.json", json_encode($data,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
        $success &= file_put_contents("../data/timestamp.json", json_encode(array('last_update' => $data['timestamp'])));
        if($success === false){
            echo '{"status":"write_error"}';
        } else {
            echo '{"status":"ok"}';
        }
    } else {
        echo '{"status":"post_data_error"}';
    }
} else {
    echo '{"status":"method_not_allowed"}';
}
?>