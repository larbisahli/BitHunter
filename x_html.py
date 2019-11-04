html_0 = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>BitHunter</title>

    <style>
        body {
            background-color: rgb(211, 211, 211);
            margin: 0;
        }

        .sidebar {
            position: fixed;
            height: 100%;
            margin-top: 10px;
        }

        .sidebar div {
            margin-top: 5px;
            height: 50px;
            padding-top: 10px;
            padding-bottom: 10px;
        }

        .sidebar div p {
            background: linear-gradient(rgb(50, 50, 50), rgb(55, 55, 55));
            color: rgb(211, 211, 211);
            padding: 15px 5px;
            font-size: 12px;
            border-radius: 0px 30px 30px 0px;
            transition: all 0.4s ease;
        }

        .sidebar div p:hover {
            background: linear-gradient(rgb(100, 100, 100), rgb(66, 66, 66));
            background-color: rgb(0, 0, 0);
            box-shadow: rgba(10, 0, 0, 0.4) 0px 2px 10px;
            transition: all 0.3s ease;
            margin-top: 9px;

        }

        .journal {
            width: 75%;
            float: right;
            margin: 10px;
        }

        table {
            font: 1em sans-serif;
            text-align: center;

            display: table;
            border-collapse: separate;
            background-color: rgb(56, 55, 55);
        }

        table thead tr th {
            padding: 8px 8px;
            color: rgb(206, 208, 212);
            border-bottom: 1px solid black;
            display: table-cell;
            background-color: rgb(48, 46, 46);
            vertical-align: top;
        }

        table tbody tr td {
            padding: 8px 8px;
            border-bottom: 1px solid black;
            display: table-cell;
            background-color: rgb(211, 211, 211);
            vertical-align: top;
        }

        .sidebar h4 {
            margin: 0px;
            padding: 5px;
        }

        html::-webkit-scrollbar {
            width: 13px;
        }

        html::-webkit-scrollbar-thumb {

            background: linear-gradient(rgb(0, 0, 0), rgb(82, 81, 81));
            color: rgb(0, 0, 0);
            border-radius: 3px;

            box-shadow: inset 2px 2px 2px rgba(255, 255, 255, .25), inset -2px -2px 2px rgba(0, 0, 0, .25);
        }

        html::-webkit-scrollbar-track {
            background: linear-gradient(to right, #dddddd, #dbdbdb 1px, #ffffff 1px, #cacac5);

        }

        @media screen and (max-width: 560px) {
            .journal {
                width: 75%;
                float: right;
                margin: 0px;
            }
        }



        @media screen and (max-width: 650px) {

            .navbar {
                display: none;
            }

            .sidebar {
                margin-top: 0px;
                color: rgb(211, 211, 211);
                display: block;
                background-color: rgb(55, 55, 55);
                height: 100%;

            }

            .sidebar div h4 {
                text-align: center;
            }

            .sidebar div p {
                border-radius: 0px;
            }

            .sidebar div {
                height: 30px;
            }

        }
    </style>

</head>
"""


def html_1(username, Pure_Profit, Total_Wins, Total_Losses, MAX_Gain, MIN_Gain, MAX_Loss, MIN_Loss, color):
    html_sidbar = f"""<body>
        <div class="sidebar">
            <div>
                <h4>{username}</h4>
            </div>
            <div>
                <p>Pure Profit: <i style="color:{color}; font-size: 12px;">+{Pure_Profit}₿ </i></p>
            </div>
            <div>
                <p>Total Wins: <i style="color:rgb(26, 219, 42); font-size: 12px;">+{Total_Wins}₿ </i></p>
            </div>
            <div>
                <p>Total Losses: <i style="color:rgb(228, 38, 31); font-size: 12px;">{Total_Losses}₿ </i></p>
            </div>
            <div>
                <p>MAX Gain: <i style="color:rgb(26, 219, 42); font-size: 12px;">+{MAX_Gain}₿</i>
                </p>
            </div>
            <div>
                <p>MIN Gain: <i style="color:rgb(26, 219, 42); font-size: 12px;">+{MIN_Gain}₿</i>
                </p>
            </div>
            <div>
                <p>MAX Loss: <i style="color:rgb(228, 38, 31); font-size: 12px;">{MAX_Loss}₿</i>
                </p>
            </div>
            <div>
                <p>MIN Loss: <i style="color:rgb(228, 38, 31); font-size: 12px;">{MIN_Loss}₿</i>
                </p>
            </div>
        </div>
       <table class="journal">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>Result</th>
                </tr>
            </thead>
    """
    return html_sidbar


def html_2(Date, Amount, Entry, Exit, Result, color):
    table = f"""
             <tbody>
                <tr>
                    <td>{Date}</td>
                    <td>{Amount}</td>
                    <td>{Entry}</td>
                    <td>{Exit}</td>
                    <td style="color: {color}; font-size: large;">{Result}</td>
                </tr>
          """
    return table


html_3 = """</tbody>
        </table>
    </body>
    </html>"""
