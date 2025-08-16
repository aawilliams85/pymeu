# ME Application Notes

Miscellaneous notes concerning ME applications themselves.

##  Lexicon
| Term   | Description
|--------|------------
| APA    | Application in archived form.
| MED    | Application in directory form.
| MER    | Application compressed into runtime form.

### MER Files
## Device Shortcuts
An ME application may have one or more Device Shortcuts to advise the terminal where to find a particular PLC.  This content is split into two files, ~/RSLinx Enterprise/SCLocal.xml and ~/RSLinx Enterprise/RSLinxNG.xml.<br><br>
The former contains a Shortcut element for each Device Shortcut.  The shortcut name and device pointer are attributes of that element.  Example:
```
  <shortcut name="SHORTCUT_1_NAME" tagfile="" sctype="" SetItemQualityBadUntilFirstWrite="" FailUnsolMsgIfDataWillBeOverwritten="" CacheUnsolicitedData="1" SendAllUnsolicitedUpdates="" CIPObject="" ShortcutPathTimeout="2" ShortcutPathCheckInterval="1" machine="" device="DRIVER_1_NAME.PLC_1_NAME" device1="">
    <aeprovider buffer_timeout="20" enabled="false"></aeprovider>
  </shortcut>
  <shortcut name="SHORTCUT_2_NAME" tagfile="" sctype="" SetItemQualityBadUntilFirstWrite="" FailUnsolMsgIfDataWillBeOverwritten="" CacheUnsolicitedData="1" SendAllUnsolicitedUpdates="" CIPObject="" ShortcutPathTimeout="2" ShortcutPathCheckInterval="1" machine="" device="1756-A17/A or B.PLC_2_NAME" device1="">
    <aeprovider buffer_timeout="20" enabled="false"></aeprovider>
  </shortcut>
```
The latter contains all of the devices/buses that were modeled on the Runtime tab for that shortcut in FactoryTalk View ME.  These elements contain attributes such as address, port number, etc.  Example:
```
	<Topology class="RSLinx.Topology" startup="99">
		<device name="FactoryTalk Linx" type="cip=77:12:115:12.1">
			<port name="Backplane" instance="1" type="65636" portNumber="1" address="256">
				<bus name="Backplane" type="cip=1:108:55"></bus>
			</port>
			<port name="Ethernet" instance="5" type="4" portNumber="5">
				<bus name="DRIVER_1_NAME" type="misc=EtherNet" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
					<port name="Port" instance="2" type="4" portNumber="2" address="192.168.1.10">
						<device name="PLC_1_NAME" type="cip=1:14:196:35" userCreated="1" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
							<port name="Backplane" instance="1" type="65645" address="0" portNumber="1">
								<bus name="1 Slot 5069 Backplane" type="cip=1:108:329" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties=""></bus>
							</port>
							<port name="PCviaUSB" instance="5" type="65643" address="16" portNumber="5">
								<bus name="17-Node USB CIP Port" type="cip=1:108:99" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties=""></bus>
							</port>
						</device>
					</port>
				</bus>
			</port>
			<port name="Ethernet 2" instance="6" type="4" portNumber="6">
				<bus name="DRIVER_2_NAME" type="misc=EtherNet" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
					<port name="A" instance="2" type="4" portNumber="2" address="192.168.1.11">
						<device name="PLC_2_ENT" type="cip=1:12:166:12" userCreated="1" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
							<port name="Backplane" instance="1" type="65537" address="1" portNumber="1">
								<bus name="1756-A17/A or B" type="cip=1:108:26" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
									<port name="Backplane" instance="1" type="65537" address="0" portNumber="1">
										<device name="PLC_2_NAME" type="cip=1:14:92:35" userCreated="1" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties="">
											<port name="PCviaUSB" instance="2" type="65643" address="16" portNumber="3">
												<bus name="17-Node USB CIP Port 3" type="cip=1:108:99" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties=""></bus>
											</port>
										</device>
									</port>
								</bus>
							</port>
							<port name="PCviaUSB" instance="3" type="65643" address="16" portNumber="3">
								<bus name="17-Node USB CIP Port 2" type="cip=1:108:99" userCreated="0" serialNumber="0" OnlineName="" NATPrivateAddress="" DataCommunicationsEnabled="1" ListIdentityExt="" MetadataInNameService="0" MetadataPassThrough="0" ConnectionInactivityTimeout="0" MaxCipConnection="1" Revision="" CatalogNumber="" ManufactureDate="" HardwareRevision="" Warranty="" Series="" ProxyProperties="" ExtendedProperties=""></bus>
							</port>
						</device>
					</port>
				</bus>
			</port>
		</device>
	</Topology>
```
pymeu attempts to combine these into an abbreviate view like this:
```
Shortcut SHORTCUT_1_NAME Topology:
├── <device name="FactoryTalk Linx" />
│   ├── <port name="Ethernet" portNumber="5" />
│   │   ├── <bus name="DRIVER_1_NAME" NATPrivateAddress="" />
│   │   │   ├── <port name="Port" address="192.168.1.10" portNumber="2" />
│   │   │   │   └── <device name="PLC_1_NAME" NATPrivateAddress="" />
Shortcut SHORTCUT_2_NAME Topology:
├── <device name="FactoryTalk Linx" />
│   ├── <port name="Ethernet 2" portNumber="2" />
│   │   ├── <bus name="DRIVER_2_NAME" NATPrivateAddress="" />
│   │   │   ├── <port name="A" address="192.168.1.11" portNumber="2" />
│   │   │   │   ├── <device name="PLC_2_ENT" NATPrivateAddress="" />
│   │   │   │   │   ├── <port name="Backplane" address="1" portNumber="1" />
│   │   │   │   │   │   ├── <bus name="1756-A17/A or B" NATPrivateAddress="" />
│   │   │   │   │   │   │   ├── <port name="Backplane" address="0" portNumber="1" />
│   │   │   │   │   │   │   │   └── <device name="PLC_2_NAME" NATPrivateAddress="" />
```