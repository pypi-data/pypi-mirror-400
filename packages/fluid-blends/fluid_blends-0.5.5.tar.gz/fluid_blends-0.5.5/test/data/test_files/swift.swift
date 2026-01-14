import CommonCrypto
import IDZSwiftCommonCrypto
import CryptoSwift
import Crypto
import IDZSwiftCommonCrypto

let cryptor = try Cryptor(operation: .encrypt, algorithm: .aes, options: .none, key: key, iv: [])
let crypt = CkoCrypt2()
crypt.CryptAlgorithm = "3des"

var name = "Tim McGraw"
let message = "Your name is \(name)"

let number = 10

if (number > 0) {
    print("Number is positive.")
}
else if (number < 0) {
    print("Number is negative")
}
else {
    print("Number is negative.")
}

let languages = ["Swift", "Java", "Go", "JavaScript"]

for language in languages {
  print(language)
}

for language in languages where language != "Java"{
  print(language)
}

// initialize the variable
var i = 1, n = 5

// while loop from i = 1 to 5
while (i <= n) {
  print(i)
   i = i + 1
}

repeat {
  print(i)
  i = i + 1
} while (i <= n)

while (i <= 10) {

  // guard condition to check the even number
  guard i % 2 == 0 else {

     i = i + 1
    continue
  }

  print(i)
  i = i + 1
}

let ageGroup = 33

switch ageGroup {
  case 0...16:
    print("Child")

  case 17...30:
    print("Young Adults")
    fallthrough

  case 31...45:
    print("Middle-aged Adults")

  default:
    print("Old-aged Adults")
}

let languages = ["Swift", "Java", "Go", "JavaScript"]

for language in languages {
  print(language)

  if language == "Java" {
    break
  }
}

// program to check pass or fail
let marks = 60

// use of ternary operator
let result = (marks >= 40) ? "pass" : "fail"

let num = 7

let result = (num == 0) ? "Zero" : ((num > 0) ? "Positive" : "Negative")

var capitalCity = ["Nepal": "Kathmandu", "England": "London"]
capitalCity["Japan"] = "Tokyo"

for (key,value) in capitalCity {
  print("\(key): \(value)")
}

func addNumbers(num1: Int, num2: Int) -> Int {
  var sum = num1 + num2
  print("Sum: ",sum)

  return sum
}

class Bike {
  var name: String
  var gear: Int

  init(name: String, gear: Int){
    self.name = name
    self.gear = gear
  }

  func calculateArea() {
    print("Double of gears =", 2 * gears)
  }
}

// create object of class
var bike1 = Bike(name: "BMX Bike", gear: 2)

bike1.gears = 11

enum Season {
  // define enum values
  case spring, summer, autumn, winter
}


enum DivisionError: Error {

  case dividedByZero
}

// create a throwing function using throws keyword
func division(numerator: Int, denominator: Int) throws {

  // throw error if divide by 0
  if denominator == 0 {
    throw DivisionError.dividedByZero
  }

  else {
    let result = numerator / denominator
    print(result)
  }
}

// call throwing function from do block
do {
  try division(numerator: 10, denominator: 0)
  print("Valid Division")
}catch DivisionError.dividedByZero {
  print("Error: Denominator cannot be 0")
}


func displayData<T>(data: T) {
  print("Generic Function:")
  print("Data Passed:", data)
}

// generic function working with String
displayData(data: "Swift")

// generic function working with Int
displayData(data: 5)

// postfix force unwrap
let url = URL(string: "https://example.com")!
