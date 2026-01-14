using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Web;
using System.Web.Http;
using System.Web.Http.OData;
using Newtonsoft.Json;
using SampleWebApi.Models;
using SampleWebApi.Repositories;
using SampleWebApi.Services;
using System.Data.SqlClient;
using System.Data;
using System.Web;
using Project = PC.MyCompany.Project;

namespace MVCWebProdem.Controllers
{
    interface ISampleInterface
    {
        void SampleMethod();
    }
}

class cipher{

  public void Encrypt(byte[] key, byte[] data, MemoryStream target)
	{
    byte[] initializationVector = new byte[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };
		using var aes = new AesCryptoServiceProvider();
		var encryptor = aes.CreateEncryptor(key, initializationVector);

  }

  public override void Bad(HttpRequest req, HttpResponse resp)
  {
    string data;
    string[] names = data.Split('-');
    int successCount = 0;
    if (data != null)
    {
      try
      {
        using (SqlConnection dbConnection = IO.GetDBConnection())
        {
          badSqlCommand.Connection = dbConnection;

          if (existingStudent != null)
          {
              existingStudent.FirstName = student.FirstName;
              existingStudent.LastName = student.LastName;

              ctx.SaveChanges();
          }
          else
          {
              return NotFound();
          }

          for (int i = 0; i < names.Length; i++)
          {
              /* POTENTIAL FLAW: data concatenated into SQL statement used in CommandText, which could result in SQL Injection */
              badSqlCommand.CommandText += "update users set hitcount=hitcount+1 where name='" + names[i] + "';";
          }
          successCount += affectedRows;
          IO.WriteLine("Succeeded in " + successCount + " out of " + names.Length + " queries.");
        }
      }
      catch (SqlException exceptSql)
      {
        IO.Logger.Log(NLog.LogLevel.Warn, "Error getting database connection", exceptSql);
      }
      finally
      {
        IO.Logger.Log(NLog.LogLevel.Warn, "Error disposing SqlCommand", exceptSql);
      }
    }
  }
}

public class Test {

  public static void main(String[ ] args) {

    int i = 0;
    while (i < 5) Console.WriteLine(i);

    while(counter < 5) {
        System.out.println("Truck number: " + counter);
        counter++;
        for(int i=1; i<=5; i++){
          System.out.println("Truck Number: " + i + ", " + counter);
          if (counter % 2 == 0){
            break;
          }else{
            continue;
          }
          System.out.println("Truck Number: " + i + ", " + counter);
      }
      if (counter > 4){
        break;
      }
      System.out.println("Finish");
    }
    switch (age) {
        case 1:  System.out.println("You are one yr old");
                 break;
        case 2:  {
                 System.out.println("You are two yr old");
                 for(int i=1; i<=5; i++){
                  System.out.println("number :" + i);
                  if (i > 3){
                    break;
                    }
                 }
                 System.out.println("Finish");
              break;
            }
        case 3:  System.out.println("You are three yr old");
                 break;
        default: System.out.println("You are more than three yr old");
                 break;
    }

    int counter = 0;
    do {
        System.out.println("Inside the while loop, counting: " + counter);
        counter++;
        for(int i=1; i<=5; i++){
          System.out.println("number :" + i);
            for(int j=1; j<=5; j++){
              int counter = 0;
              while(counter < 5) {
                if(counter==3)
                {
                  System.out.println("Breaking the for loop.");
                  break;
                }
                  System.out.println("Inside the while loop, counting: " + counter);
                  counter++;
                if (counter == 4){
                  continue;
                }
              }
              System.out.println("number :" + j);
            }
        }
    } while(counter < 5);

    try
    {
      ShowErrorMessage(result.Message);
    }
    catch (Exception)
    {
      throw;
    }
	}

  public partial class Customer{
    public string Number{
      set{
        this._Number = value;
      }
    }

    public string Name
    {
      get => _name;
      set => _name = value;
    }

    public string Email
    { get; set; }
  }

  public class CastExpr{
    IEnumerable<int> numbers = new int[] { 10, 20, 30 };
    IList<int> list = (IList<int>)numbers;
    var myValue = paidDate?.Day;
    string interpolated_var = $"{author} is an author of {book}" +
      $"The book price is ${price} and was published in year {year}";
    var student = new { Id = 1, FirstName = "James", LastName = "Bond" };
  }

  public class Startup
  {
      public void ConfigureServicesVulnerablePolicy(IServiceCollection services)
      {
          services.Configure<ForwardedHeadersOptions>(options =>
          {
              options.ForwardLimit = 1;
          });
      }
  }

  public class Example
  {
      public void Greet(string name)
      {
          string message = $"Hello {name}, welcome!";
      }
  }

  public class Person
  {
      private string name;

      public Person(string name)
      {
          this.name = name;
      }
  }
}

namespace testcases.CWE89_SQL_Injection{
	class Test_Case : AbstractTestCaseWeb {
    public override void Bad(HttpRequest req, HttpResponse resp)
    {
        string data;
        data = req.Params.Get("name");
        if (data != null)
        {
            string[] names = data.Split('-');
            int successCount = 0;
            SqlCommand badSqlCommand = null;
            try
            {
                using (SqlConnection dbConnection = IO.GetDBConnection())
                {
                    badSqlCommand.Connection = dbConnection;
                    dbConnection.Open();
                    for (int i = 0; i < names.Length; i++)
                    {
                        badSqlCommand.CommandText += "update users set hitcount=hitcount+1 where name='" + names[i] + "';";
                    }
                    var affectedRows = badSqlCommand.ExecuteNonQuery();
                    successCount += affectedRows;
                    IO.WriteLine("Succeeded in " + successCount + " out of " + names.Length + " queries.");
                }
            }
            catch (SqlException exceptSql)
            {
                IO.Logger.Log(NLog.LogLevel.Warn, "Error getting database connection", exceptSql);
            }
            finally
            {
                try
                {
                    if (badSqlCommand != null)
                    {
                        badSqlCommand.Dispose();
                    }
                }
                catch (SqlException exceptSql)
                {
                    IO.Logger.Log(NLog.LogLevel.Warn, "Error disposing SqlCommand", exceptSql);
                }
            }
        }
    }
	}

	class cipher{
  	public void Encrypt(byte[] key, byte[] data, MemoryStream target) {
    	byte[] initializationVector = new byte[] { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 };

		using var aes = new AesCryptoServiceProvider();
		var encryptor = aes.CreateEncryptor(key, initializationVector);

		using var aes2 = new AesCryptoServiceProvider();
    	var encryptor = aes2.CreateEncryptor(key, aes2.IV);

		using var cryptoStream = new CryptoStream(target, encryptor, CryptoStreamMode.Write);
		cryptoStream.Write(data);
		}
	}

	[RoutePrefix("api/house")]
    public class HouseController : ApiController
    {
        private readonly IHouseRepository _houseRepository;
        const int MaxPageSize = 10;
        private readonly IHouseMapper _houseMapper;

        public HouseController(IHouseRepository houseRepository, IHouseMapper houseMapper)
        {
            _houseRepository = houseRepository;
            _houseMapper = houseMapper;
        }

        [HttpGet]
        [EnableQuery(PageSize = MaxPageSize)]
        [Route("")]
        public IHttpActionResult Get(int page = 1, int pageSize = MaxPageSize)
        {
            if (pageSize > MaxPageSize)
            {
                pageSize = MaxPageSize;
            }

            var paginationHeader = new
            {
                totalCount = _houseRepository.GetAll().Count
                // Add more headers here if you want...
            };

            List<HouseEntity> result = _houseRepository.GetAll()
                    .Skip(pageSize * (page - 1))
                    .Take(pageSize)
                    .ToList();

            HttpContext.Current.Response.AppendHeader("X-Pagination", JsonConvert.SerializeObject(paginationHeader));

            return Ok(result.Select(x => _houseMapper.MapToDto(x)));
        }

        [HttpPost]
        [Route("")]
        public IHttpActionResult Create([FromBody] HouseDto houseDto)
        {
            if (houseDto == null)
            {
                return BadRequest();
            }

            if (!ModelState.IsValid)
            {
                return BadRequest(ModelState);
            }

            HouseEntity houseEntity = _houseMapper.MapToEntity(houseDto);

            _houseRepository.Add(houseEntity);

            return CreatedAtRoute("GetSingleHouse", new { id = houseEntity.Id }, _houseMapper.MapToDto(houseEntity));
        }

        [HttpDelete]
        [Route("{id:int}")]
        public IHttpActionResult Delete(int id)
        {
            HouseEntity houseEntityToDelete = _houseRepository.GetSingle(id);

            if (houseEntityToDelete == null)
            {
                return NotFound();
            }

            _houseRepository.Delete(id);

            return StatusCode(HttpStatusCode.NoContent);
        }
    }
}
