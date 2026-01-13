import snpvclient as sn
import os
from dotenv import load_dotenv

dotenv_path = os.path.join( os.path.dirname( __file__ ), '..', '.env' )

load_dotenv( dotenv_path=dotenv_path )

SN_HOST = os.getenv( 'SN_HOST' )
SN_USER = os.getenv( 'SN_USER' )
SN_PASSWORD = os.getenv( 'SN_PASSWORD' )

snclient = sn.SNPClient( SN_HOST )
snclient.login( SN_USER, SN_PASSWORD )

if __name__ == '__main__':

    sn.actions.list_folder( snclient )