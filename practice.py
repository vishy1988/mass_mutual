import sqlite3
import pandas as pd
from flask import *
app = Flask(__name__)
@app.route("/data",methods = ['GET','POST'])
def show_graph():
    connection = sqlite3.connect('recruit.db')
    query = "select * from customer"
    df_customer = pd.read_sql(query, connection)
    df_fb_usage = df_customer.loc[:,['race_code','facebook_user_rank']]
    df_fb_usage.facebook_user_rank = df_fb_usage.facebook_user_rank.astype(int)
    plot_df = df_fb_usage.groupby('race_code').agg({'facebook_user_rank':'mean'})
    plot_df = plot_df.reset_index()
    query = "select * from race"
    df_race = pd.read_sql(query,connection)
    df_race.columns = ['race_code','value']
    Plot_df_new = plot_df.merge(df_race,right_index=True,left_index=True,how='outer')
    Plot_df_new = Plot_df_new.drop(['race_code_x','race_code_y'],axis=1)
    Plot_df_new.columns = ['ethinicity','facebook_user_rank']
    data = Plot_df_new.to_json()
    return jsonify(data)
@app.route("/chart")
def chart_page():
    return render_template('display.html')


if __name__ == "__main__":
    app.run(app.run( port=5001),debug=True)
