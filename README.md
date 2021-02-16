# Revolut Stocks calculator for Bulgarian National Revenue Agency

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/doino-gretchenliev/revolut-stocks?label=version&sort=semver)](https://github.com/doino-gretchenliev/revolut-stocks/releases/latest)
[![GitHub Release Date](https://img.shields.io/github/release-date/doino-gretchenliev/revolut-stocks)](https://github.com/doino-gretchenliev/revolut-stocks/releases/latest)
[![GitHub issues by-label](https://img.shields.io/github/issues/doino-gretchenliev/revolut-stocks/bug)](https://github.com/doino-gretchenliev/revolut-stocks/labels/bug)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/doino-gretchenliev/revolut-stocks/Run%20tests/main?label=tests)](https://github.com/doino-gretchenliev/revolut-stocks/actions?query=workflow%3A%22Run+tests%22+branch%3Amain)
![GitHub all releases](https://img.shields.io/github/downloads/doino-gretchenliev/revolut-stocks/total)
[![Docker Pulls](https://img.shields.io/docker/pulls/gretch/nap-stocks-calculator)](https://hub.docker.com/repository/docker/gretch/nap-stocks-calculator)
[![GitHub stars](https://img.shields.io/github/stars/doino-gretchenliev/revolut-stocks)](https://github.com/doino-gretchenliev/revolut-stocks/stargazers)
![GitHub watchers](https://img.shields.io/github/watchers/doino-gretchenliev/revolut-stocks?label=watch)
[![GitHub followers](https://img.shields.io/github/followers/doino-gretchenliev?label=Follow)](https://github.com/doino-gretchenliev)
[![GitHub license](https://img.shields.io/github/license/doino-gretchenliev/revolut-stocks)](https://github.com/doino-gretchenliev/revolut-stocks/blob/main/LICENSE)

[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/fold_left.svg?style=social&label=Follow%20%40doino_gretch)](https://twitter.com/doino_gretch)

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

Note: The calculator is not natively tested on Windows OS. When using Windows it's preferable to use WSL and Docker.

#### Install dependencies

```console
$ pip install -r requirements.txt
```

#### Run (single parser)

```console
$ python stocks.py -i <path_to_input_dir> -o <path_to_output_dir>
```

#### Run (multiple parsers)

In order to use multiple parsers, you need to sort your statement files into a corresponding parser directory under the selected input directory. For example:

```console
/input-directory/revolut - directory contains Revolut statement files
/input-directory/trading212 - directory contains Trading 212 statement files
```

You can use the help command to list supported parsers with their names.

```console
$ python stocks.py -i <path_to_input_dir> -o <path_to_output_dir> -p <parser_name_1> -p <parser_name_2> ...
```

#### Help

```console
$ python stocks.py -h
```

**Output**:
```console
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

### Docker

Docker Hub images are built and published by [GitHub Actions Workflow](https://github.com/doino-gretchenliev/revolut-stocks/actions?query=workflow%3A%22Publish+Docker+image%22). The following tags are available:

* `main` - the image is built from the latest commit in the main branch.
* `<version>` - the image is built from the released version.

#### Run

```console
$ docker run --rm -v <path_to_input_dir>:/input:ro -v <path_to_output_dir>:/output gretch/nap-stocks-calculator:main -i /input -o /output
```

### Docker Compose

#### Prepare

Replace `<path_to_input_dir>` and `<path_to_output_dir>` placeholders in the `docker-compose.yml` with paths to your input and output directories.

#### Run

```console
$ docker-compose up --build
```

## Results

| Output file           | NAP mapping                                      | Description                                                               |
| --------------------- | ------------------------------------------------ | ------------------------------------------------------------------------- |
| `dec50_2020_data.xml` | `Декларация по чл.50 от ЗДДФЛ, Приложение 5 и 8` | Tax declaration - ready for import.                                       |
| `statements.csv`      | N/A                                              | Verification file to ensure correct parsing. Should be verified manually. |
| `app5-table2.csv`     | `Приложение 5, Таблица 2`                        |                                                                           |
| `app8-part1.csv`      | `Приложение 8, Част ІV, 1`                       |                                                                           |
| `app8-part4-1.csv`    | `Приложение 8, Част І`                           |                                                                           |

## Errors

Errors are being reported along with an `ERROR` label. For example:
```console
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

## Parsers

### Revolut

File format: `.pdf`

That's the default parser and handler statement files downloaded from Revolut app.

### Trading 212

File format: `.csv`

Parser for statement files, generated by Trading 212 platform. Thanks to [@bobcho](https://github.com/bobcho).

### CSV

File format: `.csv`

A generic parser for statements in CSV format. So for there, two identified usage scenarios:
1. The parser could be used with structured data from any trading platform, that could be easily organized to fit the parser's requirements.
2. The parser could be used to calculate tax information from multiple trading platforms. For example, you can generate `statements.csv` file for your Revolut activities and generate `statements.csv` file for your Trading 212 activities. Then you can append both files and process the resulted file once more. In the end, you'll receive tax information from both platforms.

In order for the file to be correctly parsed the following requirements should be met:
1. The following columns should be presented:
   1. `trade_date`: The column should contain the date of the trade in dd.MM.YYYY format.
   2. `activity_type`: The current row activity type. The following types are supported: ["SELL", "BUY", "DIV", "DIVNRA", "SSP", "MAS"]
   3. `company`: The name of the stock company. For example Apple INC.
   4. `symbol`: The symbol of the stock. For example AAPL.
   5. `quantity`: The quantity of the activity. In order to correctly recognize surrender from addition SSP and MAS activities, the quantity should be positive or negative. For all other activity types, there is no such requirement(it could be an absolute value).
   6. `price`: The activity price per share.
   7. `amount`: The total amount of the activity. It should be a result of (quantity x price) + commissions + taxes.
2. The first row should contain headers, indicating the column name, according to the mapping above. There is *no* requirement for columns to be presented in any particular order.
3. The activities, listed in the file/s should be sorted from the earliest trading date to the latest one. The earliest date should be located at the very begging of the file. When you're processing multiple statement files you can append them together(no need to merge the activities).
4. DIVNRA, which represents the tax that was paid upon receiving dividends, should follow DIV activity. Other activities could be listed between those two events. DIVNRA is not required for all DIVs but would trigger calculations for dividend tax owed to NAP. DIV activity amount should be equal to dividend value + tax.

In order to verify the parser correctness, you can compare the generated `statements.csv` file with your input file. The data should be the same in both files.

## Contribution

As this was a late-night project, improvements could be made. I'm open to new PRs.

Please submit issues [here](https://github.com/doino-gretchenliev/revolut-stocks/issues).

## Feedback

You can find me on my social media accounts:

* [Twitter](https://twitter.com/doino1990)
* [LinkedIn](https://www.linkedin.com/in/doyno-gretchenliev-60150235/)

## Support

<a href="https://www.buymeacoffee.com/doino.gretch" target="_blank">🍺 Buy Me A Beer</a>
