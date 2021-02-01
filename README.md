# Revolut Stocks calculator for Bulgarian National Revenue Agency

![Cat owe taxes joke.](https://www.thefunnybox.com/wp-content/uploads/2011/09/cat-owes-taxes.jpg)

## Information

Processing and calculating the required information about stock possession and operation is complicated and time-consuming. So that brought the idea of developing a calculator that is able to automate the process from end-to-end.

Revolut Stock calculator is able to parse Revolut statement documents and provide a ready-to-use tax declaration file(`dec50_2020_data.xml`), that you can import into NAP online system. Each part of the declaration is also exported as `csv` file for verification.

## How it works

1. The calculator recursively scans the input directory for statement files(`*.pdf`).
2. The statement files are then being parsed to extract all activity information.
3. The calculator then obtains the last published exchange rate(USD to BGN) for the day of each trade.
4. During the last step all activities are processed to produce the required data.

## Considerations

1. The calculator parses exported statements in `pdf` format. Parsing a `pdf` file is a risky task and heavily depends on the structure of the file. In order to prevent miscalculations, please review the generated `statements.csv` file under the `output` directory and make sure all activities are correctly extracted from your statement files.
2. Revolut doesn't provide information about which exact stock asset is being sold during a sale. As currently indicated at the end of each statement file, the default tax lot disposition method is `First-In, First-Out`. The calculator is developed according to that rule.
3. The trade date(instead of the settlement date) is being used for every calculation. The decision is based on the fact that the Revolut stock platform makes the cash available immediately after the initiation of a stock sale. Although the cash can't be withdrawn, it could be **used** in making other deals and so it's assumed that the transfer is finished from a user perspective.
4. By default the calculator uses locally cached exchange rates located [here](https://github.com/doino-gretchenliev/revolut-stocks/tree/main/exchange_rates). If want you can select BNB online service as exchange rates provider by enabling the `-b` flag. When activating BNB online service provider, make sure you do not spam the BNB service with too many requests. Each execution makes around 3-5 requests.
5. In application 8 part 1 you have to list all stocks, that you own by the end of the previous year(31.12.20XX). That includes stocks, that were purchased prior to the year, you're filling declaration for. There are comments in both `csv` and `xml` files to identify stock symbols along with their records. You can use those identification comments to aggregate records with data, out of the scope of the calculator.

## Requirements

* **Python** version >= 3.7
* **Docker** and **Docker Compose**(only required for Docker Compose usage option)

## Usage

### Local

#### Install dependencies

`pip install -r requirements.txt`

#### Run

`python stocks.py -i <path_to_input_dir> -o <path_to_output_dir>`

**Output**:
```sh
[INFO]: Collecting statement files.
[INFO]: Collected statement files for processing: ['input/statement-3cbc62e0-2e0c-44a4-ae0c-8daa4b7c41bc.pdf', 'input/statement-19ed667d-ba66-4527-aa7a-3a88e9e4d613.pdf'].
[INFO]: Parsing statement files.
[INFO]: Generating [statements.csv] file.
[INFO]: Populating exchange rates.
[INFO]: Generating [app8-part1.csv] file.
[INFO]: Calculating sales information.
[INFO]: Generating [app5-table2.csv] file.
[INFO]: Calculating dividends information.
[INFO]: Generating [app8-part4-1.csv] file.
[INFO]: Generating [dec50_2020_data.xml] file.
[INFO]: Profit/Loss: 1615981 lev.
```

![00s joke.](https://media.tenor.com/images/faf934d304adf3abe163e3a6d192c178/tenor.gif)

### Docker Compose

#### Prepare

Replace `<path_to_input_dir>` and `<path_to_output_dir>` placeholders in the `docker-compose.yml` with paths to your input and output directories.

#### Run

`docker-compose up --build`

## Results

| Output file           | NAP mapping                                                                      | Description                                                               |
| --------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `dec50_2020_data.xml` | `Декларация по чл.50 от ЗДДФЛ, Приложение 5 и 8`                                 | Tax declaration - ready for import.                                       |
| `statements.csv`      | N/A                                                                              | Verification file to ensure correct parsing. Should be verified manually. |
| `app5-table2.csv`     | `Приложение 5, Таблица 2`                                                        |                                                                           |
| `app8-part1.csv`      | `Приложение 8, Част ІV, 1`                                                       |                                                                           |
| `app8-part4-1.csv`    | `Приложение 8, Част І`                                                           |                                                                           |

## Errors

Errors are being reported along with an `ERROR` label. For example:
```sh
[ERROR]: Unable to get exchange rate from BNB. Please, try again later.
Traceback (most recent call last):
  File "/mnt/c/Users/doino/Personal/revolut-stocks/libs/exchange_rates.py", line 57, in query_exchange_rates
    date = datetime.strptime(row[0], BNB_DATE_FORMAT)
  File "/usr/lib/python3.8/_strptime.py", line 568, in _strptime_datetime
    tt, fraction, gmtoff_fraction = _strptime(data_string, format)
  File "/usr/lib/python3.8/_strptime.py", line 349, in _strptime
    raise ValueError("time data %r does not match format %r" %
ValueError: time data ' ' does not match format '%d.%m.%Y'
```

Please, check the latest reported error in the log for more information.

### "Unable to get exchange rate from BNB"

The error indicates that there was an issue obtaining the exchange rate from BNB online service. Please, test BNB online service manually [here](https://www.bnb.bg/Statistics/StExternalSector/StExchangeRates/StERForeignCurrencies/index.htm?search=true), before reporting an issue.

### "No statement files found"

There was an issue finding input statement files. Please, check your input directory configuration and file permissions.

### "Not activities found. Please, check your statement files"

The calculator parser was unable to parse any activities within your statement file. Please, check your statement files and ensure there are reported activities. If there are reported activities, but the error still persists, please open an issue.

### "Statements contain unsupported activity types"

The calculator found unsupported activity type/s. Please, open an issue and include the reported activity type.

### "Unable to find previously purchased shares to surrender as part of SSP"

The calculator, while trying to perform the SSP surrender shares operation, was unable to find the previously purchased shares for the same stock symbol. Please, ensure there is a statement file in the input directory, containing the original purchase.

## Import

NOTE: Importing `dec50_2020_data.xml` will clear all filling in your current tax declaration.

The `dec50_2020_data.xml` file contains applications 5 and 8. It could be imported into NAP online system with the use of NAP web interface, navigating to `Декларации, документи или данни, подавани от физически лица/Декларации по ЗДДФЛ/Декларация по чл.50 от ЗДДФЛ` and clinking on `Импорт на файл` button.

During the import, a few errors will be reported. That's normal(see exceptions below). The reason for the errors is that the imported file contains data for applications 5 and 8 only, but the system expects a complete filling of the document. After the import, you can continue filling your tax declaration as usual. Don't forget to enable applications 5 and 8 under part 3 of the main document. After you enable them you should navigate to each application, verify the data and click `Потвърди` button.

During the import, if there are reported errors in the fillings of applications 5 or 8, that's a sign of a bug in the calculator itself. Please report the error [here](https://github.com/doino-gretchenliev/revolut-stocks/issues).

## Contribution

As this was a late-night project, improvements could be made. I'm open to new PRs.

Please submit issues [here](https://github.com/doino-gretchenliev/revolut-stocks/issues).

## Feedback

You can find me on my social media accounts:

* [Twitter](https://twitter.com/doino1990)
* [LinkedIn](https://www.linkedin.com/in/doyno-gretchenliev-60150235/)

## Support

<a href="https://www.buymeacoffee.com/doino.gretch" target="_blank">🍺 Buy Me A Beer</a>
