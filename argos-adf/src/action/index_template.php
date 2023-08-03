<html>

    <body bgcolor=#99999999>
        <?php
            //ATTENTION: THIS SCRIPT REQUIRES THE PARENT DIRECTORY TO HAVE A PERMISSION OF 777 (drwxrwxrwx)

            //********** METADATA **********
            $metricName      = "%_metric_name_%";
            $metricAddress   = "%_metric_address_%";
            $anomalyTimeSt   = "%_anomaly_time_start_%";
            $anomalyTimeEd   = "%_anomaly_time_end_%";
            $detectionMet    = "%_detection_method_%";
            $detectionParams = "%_detection_parameters_%";

            //********** FILES **********
            $anomalyImageFilename = "%_anomaly_image_%";
            $statFilename         = "stat.json";

            //********** QUERY-STRNG KEYS/VALUES **********
            $reporting_k          = "reporting";
                $reporting_true_v = "true";
            $answer_k             = 'answer';
                $answer_pos_v     = 'pos';
                $answer_neg_v     = 'neg';

            //********** JSON KEYS **********
            $pos = 'pos';
            $neg = 'neg';
            $metricName_jk    = "metric_name";
            $metricAddress_jk = "metric_address";
            $anomalyTimeSt_jk = "anomaly_time_start";
            $anomalyTimeEd_jk = "anomaly_time_end";
            $detectionMet_jk  = "detection_method";

            function StoreStats($answer) {

                global $statFilename, $pos, $neg;
                global $metricName_jk, $metricName;
                global $metricAddress_jk, $metricAddress;
                global $anomalyTimeSt_jk, $anomalyTimeSt;
                global $anomalyTimeEd_jk, $anomalyTimeEd;
                global $detectionMet_jk, $detectionMet;

                if (file_exists($statFilename)) {
                    $statFile = fopen($statFilename, "r") or die ("Error: Unable to open stat file!");
                    $content = fread($statFile, filesize($statFilename));
                    fclose($statFile);
                    $jsonContent = json_decode($content, true);

                    if (strcmp($answer, $pos) == 0) {
                        $jsonContent[$pos] = $jsonContent[$pos] + 1;
                    }
                    else if (strcmp($answer, $neg) == 0) {
                        $jsonContent[$neg] = $jsonContent[$neg] + 1;
                    }
                    else {
                        die("Error: Invalid 'answer' value");
                    }

                    $statFile = fopen($statFilename, "w") or die ("Error: Unable to write stat file!");
                    fwrite($statFile, json_encode($jsonContent));
                    fclose($statFile);
                    print("<center><h2>Thank you for your response!</h2><br><h3>You may close this page.</h3></center>\n");
                }
                else {
                    $statFile = fopen($statFilename, "w") or die ("Error: Unable to create stat file!");
                    $modeResult = chmod($statFilename, 0666);
                    if (!modeResult) {
                        die ("Error: Unable to adjust mode for stat file!");
                    }
                    $jsonContent = array();
                    $jsonContent[$pos]              = 0;
                    $jsonContent[$neg]              = 0;
                    $jsonContent[$metricName_jk]    = $metricName;
                    $jsonContent[$metricAddress_jk] = $metricAddress;
                    $jsonContent[$anomalyTimeSt_jk] = $anomalyTimeSt;
                    $jsonContent[$anomalyTimeEd_jk] = $anomalyTimeEd;
                    $jsonContent[$detectionMet_jk]  = $detectionMet;

                    if (strcmp($answer, $pos) == 0) {
                        $jsonContent[$pos] = $jsonContent[$pos] + 1;
                    }
                    else if (strcmp($answer, $neg) == 0) {
                        $jsonContent[$neg] = $jsonContent[$neg] + 1;
                    }
                    else {
                        die("Error: Invalid 'answer' value");
                    }

                    fwrite($statFile, json_encode($jsonContent));
                    fclose($statFile);
                    print("<center><h2>Thank you for your response!</h2><br><h3>You may close this page.</h3></center>\n");
                }
            }

            function ReportStats($answer) {

               global $statFilename, $pos, $neg;

                if (file_exists($statFilename)) {
                    $statFile = fopen($statFilename, "r") or die ("Error: Unable to open stat file!");
                    $content = fread($statFile, filesize($statFilename));
                    fclose($statFile);
                    $jsonContent = json_decode($content, true);

                    print("Positive: " . $jsonContent[$pos] . "<br>\n");
                    print("Negative: " . $jsonContent[$neg] . "<br>\n");
                }
            }

            //********** MAIN **********
            if (strcmp($_GET[$reporting_k], $reporting_true_v) == 0) {
                ReportStats();
            }
            else if (strcmp($_GET[$answer_k], "" != 0)) {
                $answer = $_GET[$answer_k];
                if (strcmp($answer, $pos) == 0) {
                    StoreStats($pos);
                }
                else if (strcmp($answer, $neg) == 0) {
                    StoreStats($neg);
                }
                else {
                    die("Error: Invalid 'answer' value");
                }
            }
            else {
                $html = <<<HTML
                    <table cellspacing="0" cellpadding="0" border="0" align="center" width="100%">
                        <tr>
                            <td>
                                <img src="$anomalyImageFilename">&nbsp;<br>&nbsp;<br>&nbsp;<br>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <table cellspacing="0" cellpadding="0" border="1">
                                <tr><td><b>Metric name&nbsp;</b></td><td>$metricName</td></tr>
                                <tr><td><b>Metric address&nbsp;</b></td><td>$metricAddress</td></tr>
                                <tr><td><b>Anomaly time&nbsp;</b></td><td>$anomalyTimeSt&nbsp;-&nbsp;$anomalyTimeEd</td></tr>
                                <tr><td><b>Detection method&nbsp;</b></td><td>$detectionMet</td></tr>
                                <tr><td><b>Detection parameters&nbsp;</b></td><td>$detectionParams</td></tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <table cellspacing="0" cellpadding="0" border="0">
                                <tr><td><h3><p>Is this an anomaly?<br></h3></td></tr>
                                <tr><td>
                                <form action="index.php" method="GET">
                                    <input type="radio" name="answer" value="pos">Anomaly<br>
                                    <input type="radio" name="answer" value="neg">Normal<br>&nbsp;<br>
                                    <input type="submit">
                                </form>
                                </td></tr>
                                </table>
                            </td>
                        <tr>
                    </table>
HTML;
                print($html);
            }
        ?>
    </body>

</html>
