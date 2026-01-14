// First method Hello
/*
  This is a multi-line comment in Scala.
  It can be used to describe large parts of the code.
*/
/**
 * Adds two numbers and returns the result.
 *
 * @param a First number
 * @param b Second number
 * @return The sum of `a` and `b`
 */

def printfForLoop(): Unit = {
  var xyz: String = ""
  for (num <- 1 to 5) {
    xyz = s"Hello, Scala! - Iteration $num"
    println(xyz)
  }
}

def printWhileLoop(): Unit = {
  var xyz = ""
  var num = 1
  while (num <= 5) {
    xyz = s"Hello, Scala! - Iteration $num"
    println(xyz)
    num += 1
  }
}

def printDoWhileLoop(): Unit = {
  var xyz = ""
  var num = 1
  do {
    xyz = s"Hello, Scala! - Iteration $num"
    println(xyz)
    num += 1
  } while (num <= 5)
}

def checkNumber(num: Int): String = {
  num match {
    case 1 => "One"
    case 2 => "Two"
    case 3 => "Three"
    case _ => "Other"
  }
}

def sumar(a: Int, b: Int): Int = {
  return a + b
}

def dividir(a: Int, b: Int): Option[Int] = {
  try {
    Some(a / b)
  } catch {
    case e: ArithmeticException =>
      println("Error: División por cero")
      None
    case e: Exception =>
      println(s"Error inesperado: ${e.getMessage}")
      None
  } finally {
    println("Operación de división finalizada")
  }
}

import scala.collection.mutable.Queue

// Demonstrating different collection types in Scala

// Set: A collection of unique elements (duplicates are automatically removed)
val numbersSet: Set[Int] = Set(1, 2, 3, 4, 4, 5) // The duplicate '4' is ignored
println(numbersSet) // Output: Set(1, 2, 3, 4, 5)

// Vector: An immutable sequence with fast random access
val numbersVector: Vector[Int] = Vector(10, 20, 30, 40)
println(numbersVector(2)) // Output: 30 (indexing starts from 0)

// Queue: A mutable collection that follows FIFO (First-In-First-Out) order
val queue = Queue("Apple", "Banana", "Cherry")
queue.enqueue("Mango") // Adding an element to the queue
println(queue.dequeue()) // Removes and prints the first element ("Apple")
println(queue) // Output: Queue(Banana, Cherry, Mango)

// Tuple: A fixed-size collection that can hold different types of elements
val person: (String, Int, Boolean) = ("Alice", 25, false)
println(person._1) // Output: Alice (first element)
println(person._2) // Output: 25 (second element)
println(person._3) // Output: false (third element)

package com.currency_converter
import java.util.Date
import java.util._
import java.util.{HashMap => JHashMap}

// Lambda
val suma = (a: Int, b: Int) => a + b

// Define a generic trait
trait Logger {
  def log(message: String): Unit = println(s"Log: $message")
}

//field_declarations
class Greeting {
  def sayHello(): Unit = {
    println("Hello!")
  }
}
val greeting = new Greeting()
greeting.sayHello()

// Base class representing a generic user
class User

// Subclass representing an Admin user with extended privileges
class Admin extends User

object Main extends App {
    // Polymorphism: 'currentUser' is declared as a User but instantiated as an Admin
    val currentUser: User = new Admin()

    // Checking the actual type at runtime
    if (currentUser.isInstanceOf[Admin]) {
        println("User has admin privileges") // Output: User has admin privileges
    }
}


//Generic Function
def identity[T](value: T): T = value

implicit val factor: Int = 10
def multiplica(x: Int)(implicit factor: Int): Int = x * factor
println(multiplica(5))

// Lazy initialization:
lazy val slowCalculation = {
  println("Executing expensive computation...")
  10 * 2 // Simulated computation
}

// The value is not computed until it is accessed
println(slowCalculation) // Output: "Executing expensive computation..." followed by "20"


class MyClass

import scala.util.Try

class CurrencyConverter {

  // Método para convertir una cantidad usando una tasa de cambio
  def convert(
      price: Double,
      fromCurrency: String,
      toCurrency: String,
      forDate: String,
      format: String = "yyyyMMdd",
      fallback: Boolean = false
  ): Try[Double] =
    exchangeRate(fromCurrency, toCurrency, forDate, format, fallback)
      .map(_ * price)

  // Parser de línea para tasas de cambio
  private var lineParser: String => Option[ExchangeRate] =
    ExchangeRate.defaultRateLineParser

  // Supuesto método de obtención de tasa de cambio (debes implementarlo o conectarlo)
  private def exchangeRate(
      from: String,
      to: String,
      date: String,
      format: String,
      fallback: Boolean
  ): Try[Double] = {
    // Aquí debes implementar cómo se obtiene la tasa de cambio
    // Esto es solo un stub de ejemplo
    Try(1.0) // Retorna siempre 1.0 como dummy
  }
}


class HelloScala2 {
  def demonstrateVariables(): Unit = {
    val message: String = "Hello, Scala!"
    val number: Int = 12
    val decimal: Double = 12.5
    val booleanValue: Boolean = true
    val character: Char = 'A'
    val list: List[Int] = List(1, 2, 3)
    val map: Map[String, Int] = Map("one" -> 1, "two" -> 2)

    println(s"Message: $message")
    println(s"Number: $number, Decimal: $decimal, Boolean: $booleanValue, Character: $character")
    println(s"List: $list, Map: $map")
  }

  def checkCondition(message: String): Unit = {
    if (message.contains("Scala")) {
      println("The message contains the word 'Scala'.")
    } else if (message.length > 10) {
      println("The message does not contain 'Scala', but it has more than 10 characters.")
    } else {
      println("The message does not contain 'Scala' and has 10 characters or less.")
    }
  }

  def printMessage(): Unit = {
    val message = "Hello, Scala!"
    println(message)
  }

  def main2(args: Array[String]): String = {
    val message = "Hello, Scala!"
    demonstrateVariables()
    checkCondition(message)
    printMessage()
    message
  }
}

object DataParser {
  def parse(data: String): Int = {
    try {
      data.toInt
    } catch {

      case NonFatal(e) => throw e
    }
  }
}

import javax.inject.Inject

class GreetingController @Inject() (service: GreetingService) {
  def sayHello(): Unit =
    println(service.greet())
}

def myMethod(@nowarn unusedParam: Int, usedParam: Int): Int = {
  usedParam * 2
}
