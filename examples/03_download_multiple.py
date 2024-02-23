from pymeu import MEUtility
from multiprocessing import Pool

terminals = ['YourPanelViewIpAddress1', 
             'YourPanelViewIpAddress2', 
             'YourPanelViewIpAddress3']
file = 'C:\\YourFolder\\YourProgram.mer'

def download(comms_path):
    meu = MEUtility(comms_path)
    meu.download(file, overwrite=True)

if __name__ == "__main__":
    with Pool() as pool:
        result = pool.map(download, terminals)