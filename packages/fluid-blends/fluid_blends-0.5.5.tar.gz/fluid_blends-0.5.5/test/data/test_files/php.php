<?php

$page = $_GET['page'] . '.php';
require_once $page;

use Namespace\ClassName;
use Namespace\ClassName as Alias;
use function ClassName;
use const Namespace\CONSTANT_NAME;

// This is a comment
function greet($name) {
    echo "Hello, $name!";
}

class User {
    use CallableResolverAwareTrait;

    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function getName() {
        return $this->name;
    }
}

$app = new \Slim\App($c);

$user = new User("John");

// Conditional
if ($user->getName() == "John") {
    echo "Welcome back, John!";
} else {
    echo "Hello, guest!";
}

// For loop
for ($i = 0; $i < 5; $i++) {
    echo "Iteration $i\n";
    $this->Stack[$this->sp++] = 5;
    ++$countShapes[$sheetIndex];
}

// For loop pre-update
for ($i = 0; $i < 5; ++$i) {
    echo "Iteration $i\n";
}

// While loop
$i = 0;
while ($i < 5) {
    echo "Iteration $i\n";
    $i++;
}

// Foreach loop
$colors = array("red", "green", "blue");
foreach ($colors as $color) {
    echo "$color\n";
}

// Variable declaration
$message = "Hello, world!";
$token = (decrypt(str_replace("#@@#", "/", $_GET['tk'])));
echo $message;


$day = "Monday";

switch ($day) {
    case "Monday":
        echo "Today is Monday.";
        break;
    case "Tuesday":
        echo "Today is Tuesday.";
        break;
    case "Wednesday":
        echo "Today is Wednesday.";
        break;
    case "Thursday":
        echo "Today is Thursday.";
        break;
    case "Friday":
        echo "Today is Friday.";
        break;
    case "Saturday":
        echo "Today is Saturday.";
        break;
    case "Sunday":
        echo "Today is Sunday.";
        break;
    default:
        echo "Invalid day.";
        break;
}

$c['suscriptable'] = function ($c) {
    return function ($request, $response) use ($c) {
        $array = array('Status' => '404', 'Message' => 'Page not found');
        return $c['response']
            ->withStatus(404)
            ->withHeader("Content-Type", "application/json")
            ->write(json_encode($array));
    };
};

class Db
{
    const SERVER_ALREADY_RUNNING_CODE = 77;

    private $host = "localhost";
    private $db_name = "target_db";
    private $username = "some_user";
    private $password = "1HardCodedPass*";
    public $conn;
    public function getConnection()
   {
        if ($exit_code === self::SERVER_ALREADY_RUNNING_CODE) {
            $this->assertTrue(
            $recurse,
            "Typechecker still running"
            );

            exec('hh_client stop 2>/dev/null');
            $this->testTypechecks(/* recurse = */ false);
            $seriesPlot->mark->SetType(self::$markSet[$plotMarkKeys[self::$plotMark++]]);

            return;

        }
        $this->middleware[] = new DeferredCallable($callable, $this->container);
        $this->conn = null;

        $frames = Frame::$ID_COUNTER;

        $token = (decrypt(str_replace("#@@#", "/", $_GET['tk'])));



        if ($token != "") {

            $usuario = explode("#", $token)[0];
            $requestId = explode("#", $token)[1];


            include "old/validarusuariosession.php";

            $class = (setClass($usuario, $requestId));
        }

        try {
            $this->conn = new PDO("mysql:host=" . $this->host . ";dbname=" . $this->db_name, $this->username, $this->password);
            $this->conn->exec("set utf");
        } catch (PDOException $exception) {
            echo "Database conn error: " . $exception->getMessage();
        }

        return $this->conn;
    }
    function read()
    {
        $conn = Db::getConnection();
        $this->data[$key][] = $value;
        $this->data[$key]["hello"][] = $value;

        if ($limit != "") {
            $limit_str = " LIMIT " . $limit;
        }
        if ($from != "" && $to != "") {
            $limit_str = " LIMIT " . $from . "," . ($to - $from);

        }

        return $limit_str;
    }
    function update()
    {
        $contador = 0;
        foreach ($this as $child) {
            if ($child instanceof self) {
                $child->mergeSlashNodes();
                if ('/' === substr($child->prefix, -1)) {
                    $children = array_merge($children, $child->all());
                } else {
                    $children[] = $child;
                }
            } else {
                $children[] = $child;
            }
        }
        foreach ($this->data as $key => $value) {
            if ($key != "id") {
                if ($contador == 0) {
                    $upd=$upd . $key . "='".$value."'" ;
                }else{
                    $upd=$upd . ",". $key . "='".$value."'" ;
                }
                $contador ++;

            }
        }

        $target = parent::getTarget($EventType);


        switch ($EventType){
            case 9:
                $competencia_id = 1;

                break;

            case 0:
                $competencia_id = 3;

                break;

            case 1:
                $competencia_id = 9;

                break;


        }


        $query = "UPDATE
                " . $this->table_name . " a
            SET
                ". $upd ."
            WHERE
                a.proveedor_id = :id";


        $this->id = htmlspecialchars(strip_tags($this->id));

        $stmt->bindParam(':id', $this->id);

        $access = $stmt->highly->nested->member->access;

        $c['notFoundHandler'] = "SomeStr";

        return $stmt->highly->nested->member->call($query);

    }

    function evaluateExpression($expression) {

        self::update();
        global $day;
        if (!is_string($expression)) {
            throw new InvalidArgumentException('$expression must be a string');
        }
    }

    public function deleteUser(Stringable|string $uid): void
    {
        try {
            $this->client->deleteUser($uid);
        } catch (UserNotFound) {
            throw new UserNotFound("No user with uid '{$uid}' found.");
        }
    }
}

namespace named {
    class Data {

        private $name;

        public function __construct($name) {
            $this->name = $name;
        }

        public function getName() {
            return $this->name;
        }
    }
}

namespace {
    function read() {
        $this->data[$key][] = $value;
        $this->data[$key]["hello"][] = $value;

        if ($limit != "") {
            $limit_str = " LIMIT " . $limit;
        }
        if ($from != "" && $to != "") {
            $limit_str = " LIMIT " . $from . "," . ($to - $from);

        }

        return $limit_str;
    }
}

function do_offset($level)
{
    $offset = '';
    for ($i=1; $i<$level ;$i++)
        $offset = $offset . '<td></td>';
    return $offset;
}

?>
<div class="column prepend-1 span-24 first last" >
<h2> Register for an account!</h2>
<p>
Protect yourself from hackers and <a href="/passcheck.php">check your password strength</a>
</p>
<table cellspacing="0" style="width:320px">
  <form action="<?=h( $_SERVER['PHP_SELF'] )?>" method="POST">
  <tr><td>Username :</td><td> <input type="text" name="username" /></td></tr>
  <tr><td>First Name :</td><td> <input type="text" name="firstname" /></td></tr>
  <tr><td>Last Name :</td><td> <input type="text" name="lastname" /></td></tr>
  <tr><td>Password :</td><td> <input type="password" name="password" /></td></tr>
  <tr><td>Password again :</td><td> <input type="password" name="againpass" /></td></tr>
  <tr><td><input type="submit" value="Create Account!" /></td><td></td></tr>
</form>
</table>
</div>
