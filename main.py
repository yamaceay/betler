import streamlit as st
import pandas as pd
import numpy as np
from dateutil import parser
from datetime import datetime, timedelta
from shift import shift_date
import time
from driver import find_driver
import sys
import re
import lxml
import html5lib
from bs4 import BeautifulSoup
import os

def get_data(driver):
    form_dfs = []
    league_names = []
    league_abbrs = []
    driver.get("https://www.soccerstats.com/")
    time.sleep(1)
    driver.execute_script("document.querySelector('#qc-cmp2-ui > div.qc-cmp2-footer.qc-cmp2-footer-overlay.qc-cmp2-footer-scrolled > div > button.sc-ifAKCX.hIGsQq').click()")
    time.sleep(1)
    driver.execute_script("document.querySelector('#qc-cmp2-ui > div.qc-cmp2-footer > button.sc-ifAKCX.hIGsQq.qc-cmp2-hide-desktop').click()")
    for i in range(1, 31):
        elem = driver.find_element_by_css_selector("#headerlocal > div > div > div:nth-child(2) > table:nth-child(2) > tbody > tr > td:nth-child("+str(i)+") > span > a")
        league_abbr = elem.get_attribute("innerText")
        league_name = re.findall(' alt="(.*?)" ', elem.get_attribute("outerHTML"))[0]
        elem.click()
        # find the table in selenium
        try:
            table = driver.find_element_by_xpath("// *[ @ id = 'content'] / div[5] / div[3] / table[4]")
            form_df = pd.concat(pd.read_html(table.get_attribute("innerHTML")), axis=0)
        except:
            table = driver.find_elements_by_css_selector(
                "#content > div:nth-child(8) > div.eight.columns > table:nth-child(7)")[0]
            form_df = pd.concat(pd.read_html(table.get_attribute("innerHTML")), axis=0)
        league_names.append(league_name)
        league_abbrs.append(league_abbr)
        form_dfs.append(form_df)
        driver.get("https://www.soccerstats.com")
    return form_dfs

def process_data(form_dfs):
    league_offsets = [len(x) for x in form_dfs]
    names = []
    abbrs = []
    forms = pd.concat(form_dfs, axis=0)
    for i in range(len(league_offsets)):
        for x in range(league_offsets[i]):
            names.append(league_names[i])
            abbrs.append(league_abbrs[i])
    forms["league_name"] = names
    forms["league_abbr"] = abbrs
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    forms["home"] = forms.loc[:, 1].apply(lambda x: x.split(" - ")[0])
    forms["away"] = forms.loc[:, 1].apply(lambda x: x.split(" - ")[1])
    forms = forms.drop(1, axis=1)
    forms = forms[forms[2] != "-"]
    forms["home_goal"] = forms[2].apply(lambda x: x.split("-")[0])
    forms["away_goal"] = forms[2].apply(lambda x: x.split("-")[1])
    forms = forms.drop(2, axis=1)
    forms["month"] = forms[0].map(lambda x: np.argmax([x.__contains__(y) for y in months]) + 1)
    forms["day"] = re.findall("\d+", " ".join(forms[0]))
    forms["str_day"] = ["0" + str(day) if len(str(day)) == 1 else str(day) for day in forms["day"]]
    forms["str_month"] = ["0" + str(month) if len(str(month)) == 1 else str(month) for month in forms["month"]]
    forms["datetime"] = forms["str_month"] + "/" + forms["str_day"]
    forms = forms.drop([0], 1)
    forms = forms[["datetime", "home", "away", "home_goal", "away_goal", "league_name", "league_abbr"]]
    forms_index = list(forms.index)
    count_match = "".join(
        [str(int(x.strip(" ")[-1]) + 1) for x in " ".join([str(x) for x in forms_index]).split("0 ")[1:]])
    matches_list = []
    offset = 0
    for count in list(count_match):
        n_match = int(count)
        lower = offset
        upper = lower + n_match
        offset += n_match
        matches = forms.iloc[lower:upper]
        matches_list.append(matches)
        team_names = []
    for teams in matches_list:
        team_names.append(pd.Series([*list(teams["home"].values), *list(teams["away"].values)]).value_counts().index[0])
    for i in range(len(team_names)):
        matches_list[i]["team"] = [team_names[i] for x in range(len(matches_list[i]))]
    df = pd.concat(matches_list, axis=0)
    df = df.reset_index(drop=True)
    df["opponent"] = [df["away"][i] if df["team"][i] == df["home"][i] else df["home"][i] for i in range(len(df))]
    df["avg_goal"] = df["home_goal"].astype(int) - df["away_goal"].astype(int)
    df = df.drop(["home", "away"], 1)
    return df

def main ():
    if (len(sys.argv) == 1): heroku = 0
    else: heroku = int(sys.argv[1])
    driver = find_driver(heroku)
    form_dfs = get_data(driver)
    df = process_data(form_dfs)
    print(df.head(10))

if __name__ == "__main__":
    main()