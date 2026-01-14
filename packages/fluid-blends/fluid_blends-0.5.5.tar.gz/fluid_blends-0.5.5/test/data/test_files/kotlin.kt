package sast

import android.content.ContentProvider
import android.content.ContentValues
import android.content.Context
import android.content.UriMatcher
import android.database.SQLException
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import android.net.Uri
import android.support.v7.app.AppCompatActivity
import android.util.Log

import java.io.File
import java.io.FileOutputStream

const val SHIFT = 3

class AccountProvider : ContentProvider() {
    private lateinit var database: DatabaseHelper
    private val ACCOUNTS = 1
    private val sURIMatcher = UriMatcher(UriMatcher.NO_MATCH)

    init {
        sURIMatcher.addURI(AUTHORITY, ACCOUNTS_TABLE, ACCOUNTS)
        sURIMatcher.addURI(
            AUTHORITY, ACCOUNTS_TABLE + "/#", ACCOUNTS_ID
        )
    }

    fun encrypt(original: String): String {
        var encrypted: String = ""

        for (c in original) {
            val ascii: Int = c.toInt()
            val lowerBoundary: Int = if (c.isUpperCase()) 65 else 97

            if (ascii in 65..90 || ascii in 97..122) {
                encrypted += ((ascii + SHIFT - lowerBoundary) % 26 + lowerBoundary).toChar()
            } else {
                encrypted += c
            }
        }

        return encrypted
    }

    @Synchronized
    private fun installDatabaseFromAssets() {
        val inputStream = context.assets.open("$ASSETS_PATH/$DATABASE_NAME.sqlite3")

        try {
            val outputFile = File(context.getDatabasePath(DATABASE_NAME).path)
            inputStream.copyTo(FileOutputStream(outputFile))
            inputStream.close()
        } catch (exception: Throwable) {
            throw RuntimeException("The $DATABASE_NAME database couldn't be installed.", exception)
        } finally {
            return status
        }
    }

    private fun sync() {
        val username: String = PreferenceHelper.getString("userEmail", "")
        val cursor: Cursor = DatabaseHelper(applicationContext).listNotes(account.id)

        while (cursor.moveToNext()) {
            val id: Int = cursor.getInt(cursor.getColumnIndex("_id"))
            val call: Call<Void> = apiService.syncNote(basicAuth, username, id, note)

            call.enqueue(object : Callback<Void> {
                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Log.e("Sync", t.message.toString())
                }
            })
        }
    }

    override fun insert(uri: Uri, values: ContentValues): Uri? {
        val uriType = sURIMatcher.match(uri)
        val sqlDB = this.database.writableDatabase

        val id: Long
        when (uriType) {
            ACCOUNTS -> id = sqlDB.insert(ACCOUNTS_TABLE, null, values)
            else -> throw IllegalArgumentException("Unknown URI: " + uri)
        }
        context.contentResolver.notifyChange(uri, null)
        return Uri.parse(ACCOUNTS_TABLE + "/" + id)
    }

    companion object {
        private val AUTHORITY = "com.cx.vulnerablekotlinapp.accounts"
        private val ACCOUNTS_TABLE = "Accounts"
        val CONTENT_URI: Uri = Uri.parse(
            "content://" + AUTHORITY + "/" + ACCOUNTS_TABLE
        )
        private val DATABASE_NAME = "data"
    }

    val person = Person(firstName = "Alex", lastName = "Example")
    val greeting = "Hello ${person.firstName}!"
    val greeting2 = "Hello ${person}!"
}

class ServerInfoActivity : AppCompatActivity() {
    private lateinit var serverIPAddress: String
    private lateinit var serverPort: String
    val IP_ADDRESS = "ip_address"
    val PORT = "port"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_server_info)

        val prefs = applicationContext.getSharedPreferences(
            applicationContext.packageName, Context.MODE_PRIVATE
        )
        this.serverIPAddress = prefs!!.getString("ip_address", "127.0.0.1")
        this.serverPort = prefs!!.getString("port", "8080")

        var buttonSave: Button = findViewById(R.id.buttonSave)

        buttonSave.setOnClickListener {
            this.serverIPAddress = findViewById<EditText>(R.id.IPAddress).text.toString()
            this.serverPort = findViewById<EditText>(R.id.port).text.toString()

            if (
                this.serverIPAddress.isNullOrEmpty() or
                this.serverPort.isNullOrEmpty()
            ) {
                // Do nothing
                this.displayAlert()
            } else {
                val prefs = applicationContext.getSharedPreferences(
                    applicationContext.packageName, Context.MODE_PRIVATE
                )
                val editor = prefs!!.edit()
                editor.putString(this.IP_ADDRESS, this.serverIPAddress)
                editor.putString(this.PORT, this.serverPort)
                editor.apply()
            }
        }
    }

    private fun displayAlert() {
        val alert = Builder(this)
        // Builder
        with(alert) {
            setTitle("Error")
            setMessage("IP Address or Port setting is empty!")

            setPositiveButton("OK") {
                dialog, _ ->
                dialog.dismiss()
            }
        }

        // Dialog
        val dialog = alert.create()
        dialog.show()

        "Hello, World" matches "^Hello".toRegex()
    }

}

fun Application.main(dbConnection: Connection, entityManager: EntityManager) {
    routing {
        get("/articles/secure/paginated") {
            val limit = call.request.queryParameters["count"]?.toIntOrNull() ?: 10

            val sql = "SELECT * FROM articles LIMIT $limit"
            val statement = dbConnection.createStatement()
            statement.executeQuery(sql) // -> Safe
        }
    }
}
