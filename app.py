from flask import Flask, render_template, request, jsonify, redirect, url_for, json
import sqlite3 as sql

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"

# config that should come from server or updated

config = {'qty_wheels': 4,
          'power_type': {'options': 'power_types', 'default': 'petrol'},
          'power_unit': {'default': 1},
          'aux_power_type': {'options': 'aux_power_types', 'default': 'none'},
          'aux_power_unit': {'default': 1},
          'hamster_booster': {'default': 0},
          'flag_color': {'options': 'color_types', 'default': 'white'},
          'flag_patterns': {'options': 'flag_pattern_types', 'default': 'plain'},
          'flag_color_secondary': {'options': 'color_types', 'default': 'black'},
          'tyres': {'options': 'tyre_types', 'default': 'knobbly'},
          'qty_tyres': {'default': 4},
          'armour': {'options': 'armour_types', 'default': 'none'},
          'attach': {'options': 'attack_type', 'default': 'none'},
          'qty_attacks': {'default': 0},
          'fireproof': {'options': 'bool_types', 'default': 'false'},
          'insulated': {'default': 'bool_types', 'default': 'false'},
          'antibiotic': {'default': 'bool_types', 'default': 'false'},
          'banging': {'default': 'bool_types', 'default': 'false'},
          'algo': {'options': 'algo_types', 'default': 'steady'},
          'color_types': ['white', 'silver', 'gray', 'black', 'maroon', 'red', 'purple',
                          'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua'],
          'secondary_color_types': ['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple',
                                    'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua'],
          'flag_pattern_types': ['plain', 'vstripe', 'hstripe', 'dstripe', 'checker', 'spot'],
          'power_types': {'petrol': {'cost': 4},
                          'fusion': {'cost': 400},
                          'steam': {'cost': 3},
                          'bio': {'cost': 5},
                          'electric': {'cost': 20},
                          'rocket': {'cost': 16},
                          'hamster': {'cost': 3},
                          'thermo': {'cost': 300},
                          'solar': {'cost': 40},
                          'wind': {'cost': 20}
                          },
          'aux_power_types': {'none': {'cost': 0},
                              'petrol': {'cost': 4},
                              'fusion': {'cost': 400},
                              'steam': {'cost': 3},
                              'bio': {'cost': 5},
                              'electric': {'cost': 20},
                              'rocket': {'cost': 16},
                              'hamster': {'cost': 3},
                              'thermo': {'cost': 300},
                              'solar': {'cost': 40},
                              'wind': {'cost': 20}
                              },
          'tyre_types': {'knobbly': {'cost': 0},
                         'slick': {'cost': 0},
                         'steelband': {'cost': 0},
                         'reactive': {'cost': 0},
                         'maglev': {'cost': 0},
                         },
          'armour_types': {'none': {'cost': 0},
                           'wood': {'cost': 0},
                           'aluminium': {'cost': 0},
                           'thinsteel': {'cost': 0},
                           'thicksteel': {'cost': 0},
                           'titanium': {'cost': 0}
                           },
          'attack_types': {'none': {'cost': 0},
                           'spike': {'cost': 5},
                           'flame': {'cost': 20},
                           'charge': {'cost': 28},
                           'biohazard': {'cost': 30}
                           },
          'algo_types': ['steady', 'defensive', 'offensive', 'titfortat', 'random', 'buggy'],
          'bool_types': ['false', 'true']
          }

color_options = config['color_types']
secondary_color_options = config['secondary_color_types']
flag_pattern_options = config['flag_pattern_types']
power_options = list(config['power_types'].keys())
aux_power_options = list(config['aux_power_types'].keys())
tyre_options = list(config['tyre_types'].keys())
armour_options = list(config['armour_types'].keys())
attack_options = list(config['attack_types'].keys())
algo_options = config['algo_types']
bool_options = config['bool_types']

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
    if request.method == 'GET':
        return render_template("buggy-form.html",
                               buggy=None,
                               color_options=color_options,
                               secondary_color_options=secondary_color_options,
                               flag_pattern_options=flag_pattern_options,
                               power_options=power_options,
                               aux_power_options=aux_power_options,
                               tyre_options=tyre_options,
                               armour_options=armour_options,
                               attack_options=attack_options,
                               algo_options=algo_options,
                               bool_options=bool_options)

    elif request.method == 'POST':
        msg=""
        print(request.form)
        qty_wheels = request.form['qty_wheels']
        power_type = request.form['power_type']
        power_units = request.form['power_units']
        aux_power_type = request.form['aux_power_type']
        aux_power_units = request.form['aux_power_units']
        hamster_booster = request.form['hamster_booster']
        flag_color = request.form['flag_color']
        flag_pattern = request.form['flag_pattern']
        flag_color_secondary = request.form['flag_color_secondary']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attack = request.form['qty_attack']
        fireproof = request.form['fireproof']
        insulated = request.form['insulated']
        antibiotic = request.form['antibiotic']
        banging = request.form['banging']
        algo = request.form['algo']
        total_cost = 0.0

        print(f'qty_wheels = {qty_wheels}')
        print(f'power_type = {power_type}')
        print(f'power_units = {power_units}')
        print(f'aux_power_type = {aux_power_type}')
        print(f'aux_power_units = {aux_power_units}')
        print(f'hamster_booster = {hamster_booster}')
        print(f'flag_color = {flag_color}')
        print(f'flag_pattern = {flag_pattern}')
        print(f'flag_color_secondary = {flag_color_secondary}')
        print(f'tyres = {tyres}')
        print(f'qty_tyres = {qty_tyres}')
        print(f'armour = {armour}')
        print(f'attack = {attack}')
        print(f'qty_attack = {qty_attack}')
        print(f'fireproof = {fireproof}')
        print(f'insulated = {insulated}')
        print(f'antibiotic = {antibiotic}')
        print(f'banging = {banging}')
        print(f'algo = {algo}')

        # validation checks
        if not qty_wheels.isdigit():
            msg = f"Please enter a number (integer), {qty_wheels} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not power_units.isdigit():
            msg = f"Please enter a number (integer), {power_units} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not aux_power_units.isdigit():
            msg = f"Please enter a number (integer), {aux_power_units} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not hamster_booster.isdigit():
            msg = f"Please enter a number (integer), {hamster_booster} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not qty_tyres.isdigit():
            msg = f"Please enter a number (integer), {qty_tyres} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not qty_attack.isdigit():
            msg = f"Please enter a number (integer), {qty_attack} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)

        # calculate cost
        total_cost = 0
        total_cost += config['power_types'][power_type]['cost']
        total_cost += config['aux_power_types'][aux_power_type]['cost']
        if power_type == 'hamster':
            total_cost += 5 * hamster_booster
        total_cost += config['tyre_types'][tyres]['cost'] * int(qty_tyres)
        total_cost += config['armour_types'][armour]['cost']
        total_cost += config['attack_types'][attack]['cost'] * int(qty_attack)
        if fireproof == 'yes':
            total_cost += 70
        if insulated == 'yes':
            total_cost += 100
        if antibiotic == 'yes':
            total_cost += 90
        if banging == 'yes':
            total_cost += 42

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute("SELECT MAX(id) FROM buggies")
                max_id = cur.fetchone()[0]
                new_id = max_id + 1

                print(f'new_id = {new_id}')
                insert_sql = f"""
                    INSERT INTO buggies (
                        id,
                        qty_wheels,
                        power_type,
                        power_units,
                        aux_power_type,
                        aux_power_units,
                        hamster_booster,
                        flag_color,
                        flag_pattern,
                        flag_color_secondary,
                        tyres,
                        qty_tyres,
                        armour,
                        qty_attack,
                        fireproof,
                        insulated,
                        antibiotic,
                        banging,
                        algo,
                        total_cost
                    )
                    values (
                        {new_id},   
                        {qty_wheels},
                        '{power_type}',
                        {power_units},
                        '{aux_power_type}',
                        {aux_power_units},
                        {hamster_booster},
                        '{flag_color}',
                        '{flag_pattern}',
                        '{flag_color_secondary}',
                        '{tyres}',
                        {qty_tyres},
                        '{armour}',
                        {qty_attack},
                        '{fireproof}',
                        '{insulated}',
                        '{antibiotic}',
                        '{banging}',
                        '{algo}',
                        {total_cost}
                    )       
                """

                print(f'insert_sql = {insert_sql}')
                cur.execute(insert_sql)
                con.commit()
                msg = f"Record ({new_id}) successfully saved"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()

        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    records = cur.fetchall()
    return render_template("buggy.html", buggy=records, number_of_buggies=len(records))

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
# @app.route('/edit')
@app.route('/edit/<id>', methods={'GET', 'POST'})
def edit_buggy(id):
    print(f'edit_buggy id = {id}')
    print(f'request.method = {request.method}')

    if request.method == 'GET':
        con = sql.connect(DATABASE_FILE)
        con.row_factory = sql.Row
        cur = con.cursor()
        query_sql = f"SELECT * FROM buggies WHERE id = {int(id)}"
        print(f'query_sql = {query_sql}')
        cur.execute(query_sql)
        record = cur.fetchone()

        return render_template("buggy-edit.html",
                               buggy=record,
                               color_options=color_options,
                               secondary_color_options=secondary_color_options,
                               flag_pattern_options=flag_pattern_options,
                               power_options=power_options,
                               aux_power_options=aux_power_options,
                               tyre_options=tyre_options,
                               armour_options=armour_options,
                               attack_options=attack_options,
                               algo_options=algo_options,
                               bool_options=bool_options)
    elif request.method == 'POST':
        msg=""
        print(request.form)
        qty_wheels = request.form['qty_wheels']
        power_type = request.form['power_type']
        power_units = request.form['power_units']
        aux_power_type = request.form['aux_power_type']
        aux_power_units = request.form['aux_power_units']
        hamster_booster = request.form['hamster_booster']
        flag_color = request.form['flag_color']
        flag_pattern = request.form['flag_pattern']
        flag_color_secondary = request.form['flag_color_secondary']
        tyres = request.form['tyres']
        qty_tyres = request.form['qty_tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        qty_attack = request.form['qty_attack']
        fireproof = request.form['fireproof']
        insulated = request.form['insulated']
        antibiotic = request.form['antibiotic']
        banging = request.form['banging']
        algo = request.form['algo']
        total_cost = 0.0

        print(f'qty_wheels = {qty_wheels}')
        print(f'power_type = {power_type}')
        print(f'power_units = {power_units}')
        print(f'aux_power_type = {aux_power_type}')
        print(f'aux_power_units = {aux_power_units}')
        print(f'hamster_booster = {hamster_booster}')
        print(f'flag_color = {flag_color}')
        print(f'flag_pattern = {flag_pattern}')
        print(f'flag_color_secondary = {flag_color_secondary}')
        print(f'tyres = {tyres}')
        print(f'qty_tyres = {qty_tyres}')
        print(f'armour = {armour}')
        print(f'attack = {attack}')
        print(f'qty_attack = {qty_attack}')
        print(f'fireproof = {fireproof}')
        print(f'insulated = {insulated}')
        print(f'antibiotic = {antibiotic}')
        print(f'banging = {banging}')
        print(f'algo = {algo}')

        # validation checks
        if not qty_wheels.isdigit():
            msg = f"Please enter a number (qty_wheels), {qty_wheels} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not power_units.isdigit():
            msg = f"Please enter a number (power_units), {power_units} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not aux_power_units.isdigit():
            msg = f"Please enter a number (aux_power_units), {aux_power_units} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not hamster_booster.isdigit():
            msg = f"Please enter a number (hamster_booster), {hamster_booster} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not qty_tyres.isdigit():
            msg = f"Please enter a number (qty_tyres), {qty_tyres} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)
        elif not qty_attack.isdigit():
            msg = f"Please enter a number (qty_attack), {qty_attack} is not a valid integer"
            return render_template("buggy-form.html", msg=msg)

        # calculate cost
        total_cost = 0
        total_cost += config['power_types'][power_type]['cost']
        total_cost += config['aux_power_types'][aux_power_type]['cost']
        if power_type == 'hamster':
            total_cost += 5 * hamster_booster
        total_cost += config['tyre_types'][tyres]['cost'] * int(qty_tyres)
        total_cost += config['armour_types'][armour]['cost']
        total_cost += config['attack_types'][attack]['cost'] * int(qty_attack)
        if fireproof == 'yes':
            total_cost += 70
        if insulated == 'yes':
            total_cost += 100
        if antibiotic == 'yes':
            total_cost += 90
        if banging == 'yes':
            total_cost += 42

        try:
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    """
                    UPDATE buggies set 
                        qty_wheels=?,
                        power_type=?,
                        power_units=?,
                        aux_power_type=?,
                        aux_power_units=?,
                        hamster_booster=?,
                        flag_color=?,
                        flag_pattern=?,
                        flag_color_secondary=?,
                        tyres=?,
                        qty_tyres=?,
                        armour=?,
                        qty_attack=?,
                        fireproof=?,
                        insulated=?,
                        antibiotic=?,
                        banging=?,
                        algo=?,
                        total_cost=?
                    WHERE id=?             
                    """,
                    (qty_wheels, power_type, power_units, aux_power_type, aux_power_units,
                     hamster_booster, flag_color, flag_pattern, flag_color_secondary,
                     tyres, qty_tyres, armour, qty_attack, fireproof, insulated, antibiotic,
                     banging, algo, total_cost, id)

                )
                con.commit()
                print(f"Record {id} successfully updated")
                msg = f"Record {id} successfully updated"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()

        return render_template("updated.html", msg = msg)


#------------------------------------------------------------
# delete a buggy
#------------------------------------------------------------
@app.route('/delete/<id>', methods={'DELETE', 'GET'})
def delete_buggy(id):
    # id = search.data('id')
    print(f'delete_buggy id = {id}')

    con = sql.connect(DATABASE_FILE)
    cur = con.cursor()
    delete_sql = f"DELETE FROM buggies WHERE id = {int(id)}"
    print(f'delete_sql = {delete_sql}')
    cur.execute(delete_sql)
    con.commit()

    return redirect(url_for('show_buggies'))

#------------------------------------------------------------
# You probably don't need to edit this... unless you want to ;)
#
# get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    # cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
    cur.execute("SELECT * FROM buggies")

    records = cur.fetchall()
    ret_map = {}
    for r in records:
        print(f'r={r}')
        buggies = dict(zip([column[0] for column in cur.description], r)).items()
        # print(f'buggies={buggies}')
        # json_buggies = jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })
        json_buggies = json.dumps({ key: val for key, val in buggies if (val != "" and val is not None) })
        # ret.append(jsonify({ key: val for key, val in buggies if (val != "" and val is not None) }))
        # print(f'json_buggies={json_buggies}')
        ret_map[r['id']] = json_buggies
        # ret_list.append(json_buggies)
        # print(f'ret_list={ret_map}')

    print(ret_map)
    return jsonify(ret_map)

    # buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items()
    # return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0")
