<!DOCTYPE html>
    <html lang="zh-TW">
        <head>
            <meta charset="UTF-8">
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                table, td, th {
                    border: 1px solid black;
                    padding: 5px;
                }

                th {text-align: left;}
            </style>
        </head>
        <body>

    <?php
    
    // 定義資料庫資訊
    $DB_NAME = "php";
    $DB_USER = "root";
    $DB_PASS = "mysql";
    $DB_HOST = "localhost";
                
    // 連接 MySQL 資料庫伺服器
    $con = mysqli_connect($DB_HOST, $DB_USER, $DB_PASS);
    if (empty($con)) {
        print mysqli_error($con);
        die("資料庫連接失敗！");
        exit;
    }
    
    // 選取資料庫
    if (!mysqli_select_db($con, $DB_NAME)) {
        die("選取資料庫失敗！");
    }
    
    // 設定連線編碼
    mysqli_query($con, "SET NAMES 'UTF-8'");
    
    // 顯示表頭
    echo "<table>
    <tr>
    <th>文章編號</th>
    <th>文章標題</th>
    <th>文章內文</th>
    <th>發表時間</th>
    </tr>";
    
    if (isset($_GET['s'])) { // 如果有搜尋文字顯示搜尋結果
    
        $s = mysqli_real_escape_string($con, $_GET['s']);
        $sql = "SELECT * FROM search WHERE post_title LIKE '%" . $s . "%' OR post_context LIKE '%" . $s . "%'";
        $result = mysqli_query($con, $sql);
    
        // SQL 搜尋錯誤訊息
        if (!$result) {
            echo ("錯誤：" . mysqli_error($con));
            exit();
        }
    
        // 搜尋無資料時顯示「查無資料」
        if (mysqli_num_rows($result) <= 0) {
            echo "<tr><td colspan='4'>查無資料</td></tr>";
        }
    
        // 搜尋有資料時顯示搜尋結果
        while ($row = mysqli_fetch_array($result)) {
            echo "<tr>";
            echo "<td>" . $row['post_id'] . "</td>";
            echo "<td>" . $row['post_title'] . "</td>";
            echo "<td>" . $row['post_context'] . "</td>";
            echo "<td>" . $row['post_date'] . "</td>";
            echo "</tr>";
        }
    
    } else { // 如果沒有搜尋文字顯示所有資料
    
        $sql = "SELECT * FROM search";
        $result = mysqli_query($con, $sql);
    
        if (!$result) {
            echo ("錯誤：" . mysqli_error($con));
            exit();
        }
    
        while ($row = mysqli_fetch_array($result)) {
            echo "<tr>";
            echo "<td>" . $row['post_id'] . "</td>";
            echo "<td>" . $row['post_title'] . "</td>";
            echo "<td>" . $row['post_context'] . "</td>";
            echo "<td>" . $row['post_date'] . "</td>";
            echo "</tr>";
        }
    
    }
    
    echo "</table>";
    
    mysqli_close($con); // 連線結束
    
    ?>

</body>

</html>