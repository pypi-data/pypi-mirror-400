from chemparse import parse_formula
from IPython.display import SVG
import numpy as np
import pandas as pd
import pubchempy as pcp
from rdkit import Chem
import matplotlib.pyplot as plt
import random
from rdkit.Chem import rdDepictor, Draw
from rdkit.Chem.Draw import rdMolDraw2D
import statsmodels.api as sm # for multilinear regression
from aqorg import *
from pychnosz import reset, entropy
from wormutils import import_package_file, Error_Handler

class PropFit(Estimate):
    
    """
    Regress thermodynamic properties of molecular groups for use in estimation of compounds with no experimental data.
    
    Parameters
    ----------
    filename : str
        Name of csv with compound names and thermodynamic properties you want to regress.

    props : list of strings
        Thermodynamic properties you want to regress group data for. Must match the property columns in the input file. 
    """
    
    def __init__(self, filename=None, props=['Gh','Hh','Cph','V','Hig','Sig','Cpig'], group_file=None): 

        if isinstance(filename, str):
            self.input_df = pd.read_csv(filename)

        else:
            with import_package_file(__name__, 'default databases/default database.csv', as_file=True) as path:
                self.input_df = pd.read_csv(path)
                
        if isinstance(group_file, str):
            self.group_df = pd.read_csv(group_file)
        else:
            self.group_df = None
                    
        self.props = props
        self.smiles = None
        self.err_handler = Error_Handler(clean=False)
        
    def dataprep(self, average=True, order=2, output_name = None):
    
        """
        Prepare a dataframe that consists of molecule names, properties, and group match data.
        
        Parameters
        ----------
        average : bool, default True
            Average repeat measurements for compound properties?
    
        order : numeric or str, default 2
            Order of approximation for splitting molecules into groups. Accepts "2", 2, "1", 1, or 'custom'. 
            If 'custom', you must provide a group matching csv named 'custom groups.csv'.  
    
        output_name : str, default 'properties and groups.csv'
            Name of the CSV file that will be generated. 
        """
        input_df = self.input_df
        smile_df = input_df.copy()
        if output_name == None:
            output_name = 'properties and groups.csv'
        else:
            output_name = output_name

        for c in list(input_df.columns)[1:]:
            if c not in self.props:
                input_df.drop(c, axis=1, inplace=True)
                
        if average==True:
            new_df = pd.DataFrame(columns = input_df.columns)
            for i in input_df.index:
                c = input_df.loc[i, 'compound']
                if c not in list(new_df.compound):
                    new_df.loc[i, 'compound'] = c
                    for p in self.props:
                        temp_df = input_df.loc[input_df['compound'] == c].loc[~input_df[p].isnull()]
                        if len(temp_df)>0:
                            new_df.loc[i, p] = np.nanmean(temp_df[p])
            input_df = new_df

        if isinstance(self.group_df, pd.DataFrame):
            group_df = self.group_df
        elif order == 1 or order == '1':
            with import_package_file(__name__, 'default databases/1st order groups.csv', as_file=True) as path:
                group_df = pd.read_csv(path)
        elif order == 2 or order == '2':
            with import_package_file(__name__, 'default databases/2nd order groups.csv', as_file=True) as path:
                group_df = pd.read_csv(path)
        
        group_df.replace(np.nan, '', inplace=True)
        self.group_df = group_df

        keys = list(group_df['keys'])
        values = list(group_df['values'])
        pattern_dict = dict(zip(keys, values))
        for key in pattern_dict:
            if str(pattern_dict[key]) == 'nan':
                pattern_dict[key] = ''

        self.pattern_dict = pattern_dict
        
        keys += ['formula']
        df = pd.DataFrame(columns = ['compound']+keys)
        vetted_mol = []
        ind = 0

        molecules = list(input_df["compound"])
        for molecule in molecules:
            if molecule not in vetted_mol:
                self.name = molecule

                temp_smile_df = smile_df.loc[smile_df['compound']==molecule].loc[~smile_df['SMILES'].isnull()].copy()
                if len(temp_smile_df)>0:
                    self.smiles = temp_smile_df['SMILES'].values[0]
                else:
                    self.pcp_compound = pcp.get_compounds(self.name, "name")
                    self.smiles = self.pcp_compound[0].connectivity_smiles
                
                self.get_mol_smiles_formula_formula_dict()
                temp_dict = self.match_groups()
                values = list(temp_dict.values())
                temp_df = pd.DataFrame(columns = ['compound']+keys)
                temp_df.loc[0, 'compound'] = molecule
                temp_df.loc[0, keys] = values
                df = pd.concat([df, temp_df])
                vetted_mol.append(molecule)

        failures = len(vetted_mol) - len(molecules)
        if failures > 0:
            print('There were '+str(failures)+' molecules that did not work')
            print([m for m in molecules if m not in vetted_mol])

        ### now add props
        key_df = pd.DataFrame(columns = keys)
        for k in keys:
            key_df[k] = [np.nan]*len(input_df)
        prop_df = pd.concat([input_df, key_df], axis=1)
        prop_df['formula'] = prop_df['formula'].astype(str)

        prop_df = prop_df.loc[~prop_df['compound'].isnull()]        
        for i in prop_df.index:
            compound = prop_df.loc[i, 'compound']
            values = list(df.loc[df['compound'] == compound][keys].values[0])
            prop_df.loc[i, keys] = values
    
        prop_df.to_csv(output_name, index=False)
        print(output_name + ' created')
    
    def group_property_estimator(self, filename, props=None, ignore = None):
        
        """
        Regress the properties of group matches based on thermodynamic properties of molecules and molecular group matches.
        
        Parameters
        ----------
        filename : str
            Name of the file containing compounds, properties, and group matching data. 
    
        props : list of strings
            Thermodynamic properties you want to regress group data for. Must match the property columns in the input file. 
    
        ignore : list of strings
            Name of columns in the input file which are not thermodynamic properties and therefore should not be regressed. 
        """
        if not isinstance(props, list):
            props=self.props

        df1 = pd.read_csv(filename)
        
        if isinstance(ignore, list):
            df1.drop(ignore, axis=1, inplace=True)

        bad_props = []
        for p in props:
            if p not in list(df1.columns):
                bad_props.append(p)
                
        props = [p for p in props if p not in bad_props]
            
        for dependent_param in props:
            df_data = df1.copy()
            
            # remove columns containing 0 groups
            df_data = df_data.loc[:, (df_data != 0).any(axis=0)]
        
            # get data subset that needs a prediction
            df_topred = df_data[np.isfinite(df_data[dependent_param]) == False]
            
            # get data subset that does not need a prediction
            df_not_topred = df_data[np.isfinite(df_data[dependent_param]) == True]
            
            # delete rows representing compounds that need a prediction when they contain a group that is not
            # represented in the training set.
            delrows = []
            for col in df_not_topred.columns.values:
                try:
                    if sum(df_not_topred[col]) == 0:
                        for row in df_topred.index.values:
                            if df_topred.loc[row, col] != 0:
                                delrows.append(row)
                except:
                    pass
            bad_df = df_topred.index.isin(delrows)
            df_topred = df_topred[~bad_df]
            
            # remove rows without y values
            df_data = df_data[np.isfinite(df_data[dependent_param])]
        
            X = df_data[[x for x in list(df_data.columns.values) if not x in ["compound", "formula", dependent_param]+props]].copy()
            y = df_data[dependent_param].copy()
            X_topred = df_topred[[x for x in list(df_topred.columns.values) if not x in ["compound", "formula", dependent_param]+props]].copy()

            if 'ig' not in dependent_param:
                
                ## add material point
                X.loc[:, "material point"] = [1]* len(X)
                X_topred.loc[:, "material point"] = [1]* len(X_topred)
                
            multi_reg = sm.OLS(y[0:], X[0:]).fit() # perform the multiple regression
            prediction = multi_reg.predict(X) # make the predictions from the multi_reg
            preds = multi_reg.predict(X_topred)
            
            material_point = 0 
            material_point_err = 0
                
            group_property_dict = dict(zip(X.columns.values, [round(val, 4) for val in multi_reg.params.values]))
            group_property_se_dict = dict(zip(X.columns.values, [round(val, 4) for val in multi_reg.bse.values]))
            pred_errs = [sum([n_group*group_property_se_dict[group]**2 for n_group, group in zip(X.loc[idx], X.columns.values)])**0.5 for idx in X.index]
            topred_errs = [sum([n_group*group_property_se_dict[group]**2 for n_group, group in zip(X_topred.loc[idx], X_topred.columns.values)])**0.5 for idx in X_topred.index]
            
            comp_pred_df = pd.DataFrame({"compound":list(df_data["compound"]),
                                         "actual":df_data[dependent_param],
                                         "prediction":[round(pred+material_point, 2) for pred in prediction.values],
                                         "pred errs":[round(err, 2) for err in pred_errs]})
            
            df_preds = pd.DataFrame({"compound":list(df_topred["compound"]),
                                        "actual":df_topred[dependent_param],
                                         "prediction":[round(pred+material_point, 2) for pred in preds.values],
                                         "pred errs":[round(err, 2) for err in topred_errs]})
            
            df_final = pd.concat([comp_pred_df,df_preds]) #is this happening on the right axis?
            
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                df_group_property = pd.DataFrame(group_property_dict.items(), columns=['group', 'value'])
                df_group_se = pd.DataFrame(group_property_se_dict.items(), columns=['group', 'std err'])

            save_as = filename.split('.csv')[0]+' regressed'

            df_final.to_csv(save_as+"_"+dependent_param+".csv", index=False)
            df_group_property.to_csv(save_as+"_"+dependent_param+"_group_property.csv", index=False) #reports 0s when not able to estimate
            df_group_se.to_csv(save_as+"_"+dependent_param+"_group_se.csv", index=False)

    def generate(self, filename = 'properties and groups regressed', order=2, hyd_props = ['Gh','Hh','Cph','V'], gas_props = ['Hig','Sig','Cpig']):
        
        """
        Generate the group thermodynamic property databases needed to put into AqOrg's Estimate() function.
        
        Parameters
        ----------
        filename : str, default 'properties and groups regressed'
            Common start to filenames that were generated in the group_property_estimaor() function. 
    
        order : numeric or str, default 2
            Order of approximation for splitting molecules into groups. Accepts "2", 2, "1", 1, or 'custom'. 
            If 'custom', you must provide a group matching csv named 'custom groups.csv'.
            This has to match the order which was used to make the properties and groups dataframe. 
            
        hyd_props : list of strings, default ['Gh','Hh','Cph','V']
            Thermodynamic properties of hydration you want to regress group data for. Must match the property columns in the input file. 

        gas_props : list of strings, default ['Hig','Sig','Cpig']
            Thermodynamic properties of formation of ideal gases you want to regress group data for. Must match the property columns in the input file.

        """
        save_as = filename
        hyd_cols = []
        for h in hyd_props:
            hyd_cols += [h, h+'_err', h+'_n']

        gas_cols = []
        for g in gas_props:
            gas_cols += [g, g+'_err', g+'_n']

        group_df = self.group_df
    
        keys = list(group_df['keys'])
        values = list(group_df['values'])
        pattern_dict = dict(zip(keys, values))
        for key in pattern_dict:
            if str(pattern_dict[key]) == 'nan':
                pattern_dict[key] = ''

        self.pattern_dict = pattern_dict
        
        hyd = pd.DataFrame(columns = ['group']+hyd_cols+['smarts','elem'])
        temp_df = pd.read_csv(save_as+'_'+hyd_props[0]+'_group_property.csv')
        for i in temp_df.index:
            group = temp_df.loc[i, 'group']
            hyd.loc[i, 'group'] = group
            hyd.loc[i, 'smarts'] = group
            if group != 'material point':
                hyd.loc[i, 'elem'] = self.pattern_dict[group]

        group_df = pd.read_csv(save_as.split(' regressed')[0]+'.csv')
        ind = max([list(group_df.columns).index(p) for p in self.props])+1  
        end = list(group_df.columns).index('formula')
        groups = list(group_df.columns)[ind:end]

        remove = []
        for p in hyd_props:
            prop_df = pd.read_csv(save_as+'_'+p+'_group_property.csv')
            err_df = pd.read_csv(save_as+'_'+p+'_group_se.csv')
            for i in prop_df.index:
                group = prop_df.loc[i, 'group']
                value = prop_df.loc[i, 'value']
                if err_df.loc[i, 'group'] != group:
                    print('err')
                if value == 0 and i not in remove:
                    remove.append(i)
                if value != 0:
                    err = err_df.loc[i, 'std err']
                    cnt = 0
                    if group != 'material point':
                        cnt = group_df.loc[group_df[group]>0][p].count()                        
                    hyd.loc[i, p] = value
                    hyd.loc[i, p+'_err'] = err
                    hyd.loc[i, p+'_n'] = cnt
        hyd.drop(remove, inplace=True)

        gas = pd.DataFrame(columns = ['group']+gas_cols+['smarts','elem'])
        temp_df = pd.read_csv(save_as+'_'+gas_props[0]+'_group_property.csv')
        for i in temp_df.index:
            group = temp_df.loc[i, 'group']
            gas.loc[i, 'group'] = group
            gas.loc[i, 'smarts'] = group
            if group != 'material point':
                gas.loc[i, 'elem'] = self.pattern_dict[group]
    
        remove = []
        for p in gas_props:
            prop_df = pd.read_csv(save_as+'_'+p+'_group_property.csv')
            err_df = pd.read_csv(save_as+'_'+p+'_group_se.csv')
            for i in prop_df.index:
                group = prop_df.loc[i, 'group']
                value = prop_df.loc[i, 'value']
                if err_df.loc[i, 'group'] != group:
                    print('err')
                if value == 0 and i not in remove:
                    remove.append(i)
                if value != 0:
                    err = err_df.loc[i, 'std err']
                    cnt = 0
                    if group != 'material point':
                        cnt = group_df.loc[group_df[group]>0][p].count()                        
                    gas.loc[i, p] = value
                    gas.loc[i, p+'_err'] = err
                    gas.loc[i, p+'_n'] = cnt
        gas.drop(remove, inplace=True)
        gas.insert(1, 'Gig', np.nan)

        for i in gas.index:
            elements = gas.loc[i, 'elem']
            if str(elements) not in ['nan', '']:
                reset(messages=False)
                Selem = entropy(elements)
                Sig = gas.loc[i, 'Sig']
                dS = Sig - Selem
                gas.loc[i, 'Gig'] = round((gas.loc[i, 'Hig']*1000 - 298.15*dS)/1000, 3)

        gas_ind = max(gas.index)+1
        gas.loc[gas_ind, :] = 0
        gas.loc[gas_ind, 'group']='Yo'
        gas.loc[gas_ind, 'smarts']='Yo'

        hyd_ind = hyd.loc[hyd['group']=='material point'].index[0]
        hyd.loc[hyd_ind, 'group']='Yo'
        hyd.loc[hyd_ind, 'smarts']='Yo'

        gas.to_csv('gas props.csv', index=False)
        hyd.to_csv('hyd props.csv', index=False)
        
    def tts(self, repeats = 100, test_size = 0.2, filename = None, output_name = 'stats df.csv', show=True):

        """
        Perform a train-test split on the thermodynamic data you will regress and estimate properties from. 
        
        Parameters
        ----------
        repeats: int, default 100
            Number of semi-random iterations of train-test splitting to do. The iterations will be used to calculate statistics associated with the semi-random sampling process.     

        test_size: float, default 0.2
            Fraction of the database for each thermodynamic property that should be used as the test set.  
        
        filename : str, default properties and groups.csv
            Common start to filenames that were generated in the group_property_estimaor() function. 

        output_name : str, default 'stats df.csv'
            Name of the CSV file that will be generated, composed of the average and standard deviation of the RMSEs of estimations associated with each iterations. 

        show : bool, default True
            Show barplot for training and test data for each property? 
        """
        if filename == None:
            filename = 'properties and groups.csv'
        
        df = pd.read_csv(filename)
        stats_df = pd.DataFrame()
        for prop_ind, p in enumerate(self.props):
            temp_props = self.props.copy()
            temp_props.remove(p)
            prop_df = df.loc[~df[p].isnull()].drop(temp_props, axis=1)
            prop_df.reset_index(inplace=True, drop=True)
            for c in prop_df.columns[2:-1]:
                if sum(prop_df[c]) == 0:
                    prop_df.drop(c, axis=1, inplace=True)
    
            groups = list(prop_df.columns)[2:-1]
            data_len = len(prop_df)
            prop = prop_df.columns[1]
            compounds = []
            for c in list(prop_df['compound']):
                if c not in compounds:
                    compounds.append(c)
    
            ### sorting by least represented groups to make sampling easier below
            lengths = []
            for g in groups:
                length = len(prop_df.loc[prop_df[g]>0]) #how many times is the group represented
                lengths.append(length)
            length_df = pd.DataFrame()
            length_df['groups'] = groups
            length_df['lengths'] = lengths
            length_df.sort_values(by = 'lengths', inplace=True) #least common groups first
            groups = list(length_df['groups'])
        
            ### choosing one rep per group
            reps = []
            for g in groups:
                mols_w_data = []
                temp_df = prop_df.loc[prop_df[g]>0].loc[~prop_df['compound'].isin(reps)]
                if len(temp_df)>0:
                    for c in temp_df.compound:
                        if c not in mols_w_data:
                            mols_w_data.append(c)
                    reps.append(random.sample(mols_w_data, 1)[0])
            non_reps = [c for c in compounds if c not in reps]
            train = reps.copy()
            test = non_reps.copy()
        
            test_df = prop_df.loc[prop_df['compound'].isin(test)]
            train_df = prop_df.loc[prop_df['compound'].isin(train)]
        
            test_df.to_csv(p+'_test.csv', index=False) 
            train_df.to_csv(p+'_train.csv', index=False) 
    
            train_RMSEs = []
            test_RMSEs = []
            
            for r in range(0, repeats):
        
                test_df = pd.read_csv(p+'_test.csv')
                train_df = pd.read_csv(p+'_train.csv') ## bare min training set so all groups are represented
                total_df = pd.concat([train_df, test_df], ignore_index=True)
                
                compounds = []
                test = []
                train = []
                for j in total_df.index:
                    compound = total_df.loc[j, 'compound']
                    if compound not in compounds:
                        compounds.append(compound)
                        if compound in list(test_df['compound']) and compound not in test:
                            test.append(compound)
                        if compound in list(train_df['compound']) and compound not in train:
                            train.append(compound)
                            
                ## randomly harvesting more data for training set
                for i in range(0, len(test)):
                    if len(total_df.loc[total_df['compound'].isin(test)])/len(total_df) > test_size:
                        rand = random.sample(test, 1)[0]
                        train.append(rand)
                        test.remove(rand)
        
                test_df = total_df.loc[total_df['compound'].isin(test)]
                for i in test_df.index:
                    test_df.loc[i, prop] = np.nan    
                train_df = total_df.loc[total_df['compound'].isin(train)]
                
                total_df = pd.concat([train_df, test_df])
                file_name = 'split_'+p+'_test.csv'
                total_df.to_csv(file_name, index=False)
                save_as = file_name.split('.csv')[0]+' regressed'
                sig_figs = 3
                fixed_material_point = False 
                estimate_material_point = True
                self.group_property_estimator(file_name, [p])
                
                SEs=[]
                df3 = pd.read_csv(save_as+'_'+p+'.csv')
                df3 = df3.loc[~df3['actual'].isnull()]
                for c in train:
                    temp_df=df3.loc[df3['compound']==c]
                    actual=np.average(temp_df['actual'].values)
                    pred = temp_df['prediction'].values[0]
                    SEs.append((pred-actual)**2)
                train_RMSE = np.sqrt(np.nanmean(SEs))
                train_RMSEs.append(train_RMSE)
        
                df3 = pd.read_csv('split_'+p+'_test regressed_'+p+'.csv')
                df3 = df3.loc[df3['actual'].isnull()].loc[~df3['prediction'].isnull()]
                comps = []
                for k in df3.index:
                    c = df3.loc[k, 'compound']
                    if c not in comps:
                        comps.append(c)
                        
                SEs = []
                for c in comps:
                    pred = df3.loc[df3['compound'] == c]['prediction'].values[0]
                    actual = np.nanmean(df.loc[df['compound'] == c][p])
                    SEs.append((pred-actual)**2)
            
                test_RMSE = np.sqrt(np.nanmean(SEs))
                test_RMSEs.append(test_RMSE)
            
            dataset1 = []
            dataset2 = []
            stats_df.loc[prop_ind, 'property'] = p
            dataset1.append(np.array(train_RMSEs))
            dataset2.append(np.array(test_RMSEs))
            avg1 = np.nanmean(train_RMSEs)
            avg2 = np.nanmean(test_RMSEs)
            stdev1 = np.std(train_RMSEs)
            stdev2 = np.std(test_RMSEs)
            stats_df.loc[prop_ind, 'train avg'] = avg1
            stats_df.loc[prop_ind, 'train stdev'] = stdev1
            stats_df.loc[prop_ind, 'test avg'] = avg2
            stats_df.loc[prop_ind, 'test stdev'] = stdev2
            
        stats_df.to_csv(output_name, index=False)
    
        if show == True:

            colors = ['lightblue','orange','red','blue','sienna','pink','gold','navy','black']
            fig, ax = plt.subplots(1, len(self.props), figsize=(len(self.props)*2, 2))

            for n, p in enumerate(self.props):
                test_val = stats_df.loc[n, 'test avg']
                train_val = stats_df.loc[n, 'train avg']
                test_err = stats_df.loc[n, 'test stdev']
                train_err = stats_df.loc[n, 'train stdev']
                ax[n].bar(0, train_val, yerr = train_err, capsize=5, color=colors[n], label='train', edgecolor='black')
                ax[n].bar(1, test_val, yerr = test_err, capsize=5, color=colors[n], label='test', edgecolor='black', alpha=0.5, hatch='//')
                ax[n].set_title(self.props[n])
                ax[n].set_xticks([0, 1], ['train', 'test'])
            fig.suptitle('Train test splitting thermodynamic properties', y=1.1)
            ax[0].set_ylabel('RMSE')
            fig.subplots_adjust(wspace=0.3)
            plt.savefig('train test split barplots.pdf', bbox_inches='tight')