from pathlib import Path
from skimage.io import imread
import xml.etree.ElementTree as ET
import re

class PhenixReader:
    """Reader to interact with Opera Phenix datasets

    PhenixReader is a class to read in and interact with Opera Phenix datasets.

    :param filepath: Path to the top-level directory of the dataset
    :type filepath: str

    :ivar num_wells: Number of wells in the dataset
    :type num_wells: int
    """

    # XML namespace
    ns = {'v7': '43B2A954-E3C3-47E1-B392-6635266B0DD3/HarmonyV7'}

    def __init__(self, filepath):
        """Constructor method
        """

        self.filepath = Path(filepath)

        # Attempt to determine data format
        if (self.filepath / 'Images').is_dir():
            self.format = 'legacy'
            self._image_filepath = (self.filepath / 'Images')
        elif (self.filepath / 'hs').is_dir():
            self.format = 'new'
            for item in (self.filepath / 'hs').iterdir():
                if item.is_dir():
                    self._image_filepath = item
                    break
            
        else:
            raise TypeError(f"{self.filepath} does not seem to be a valid Opera Phenix image archive.")
        
        # Read metadata tree
        self._metadata_root = self.__read_metadata_xml()

        # Populate other properties
        self.num_wells = self.__count_wells()

    def __read_metadata_xml(self):
        """Read in metadata XML and return the document root

        This function reads in the "Index.xml" files and returns the document root object.
        
        :param self: Object reference

        :return: The root object
        :rtype: xml.Element
        """

        match self.format:
            case 'legacy':
                tree = ET.parse(self._image_filepath / 'Index.xml')
                return tree.getroot()
                
            case 'new':                
                for item in (self._image_filepath).iterdir():
                    if item.name.endswith('.xml'):
                        tree = ET.parse(item)
                        return tree.getroot()

            case _:
                raise ValueError("Accepted formats are 'legacy' or 'new'.")

    def __count_wells(self):
        """Count number of wells in dataset

        The number of wells is determined by counting the number of <Well> tags in the path <root>/<Plates>/<Plate>/
        
        :param self: Object reference

        :return: Number of wells
        :rtype: int
        """

        return len(self._metadata_root.findall('./v7:Plates/v7:Plate/v7:Well', self.ns))
    
    def __get_image_xml_node(self, row, col, timepoint, field=1, channel=1, plane=1):

        image_id = f"{row:02d}{col:02d}K{timepoint}F{field}P{plane}R{channel}"

        image_node = self._metadata_root.find(f".//v7:Image[v7:id = '{image_id}']", self.ns)

        if image_node is not None:
            return image_node
        else:
            raise AttributeError("The specified image node was not found")
    
    def __get_image_xml_node_byID(self, image_id):

        image_node = self._metadata_root.find(f".//v7:Image[v7:id = '{image_id}']", self.ns)

        if image_node is not None:
            return image_node
        else:
            raise AttributeError("The specified image node was not found")

    def __get_well_xml_node(self, row, col):

        well_id = f"{row:02d}{col:02d}"

        well_node = self._metadata_root.find(f".//v7:Well[v7:id = '{well_id}']", self.ns)

        if well_node is not None:
            return well_node
        else:
            raise AttributeError("The specified well node was not found")

    def get_image_metadata(self, row, col, timepoint, field=1, channel=1, plane=1):
        """Returns image metadata
        
        :param row: Well row
        :param col: Well column
        :param timepoint: Timepoint of image
        :param field: Image field of view
        :param channel: Image channel
        :param plane: Image focal plane

        :return: Image metadata
        :rtype: dict
        """

        image_node = self.__get_image_xml_node(row, col, timepoint, field, channel, plane)

        # Return a dictionary
        image_metadata = {}
        for child in image_node:
            _, tag_clean = child.tag.split('}')
            image_metadata[tag_clean] = child.text

        return image_metadata

    def read_image(self, row, col, timepoint, field=1, channel=1, plane=1):
        """Read specified image
        
        :param self: Description
        :param row: Description
        :param col: Description
        :param timepoint: Description
        :param field: Description
        :param channel: Description
        :param plane: Description
        """

        # Determine image location
        image_metadata = self.get_image_metadata(row, col, timepoint, field, channel, plane)
        image_url = image_metadata['URL']

        # Read image file
        image = imread((self._image_filepath / image_url))
        
        return image

    def image_iter_time(self, row, col, field=1, channel=1, plane=1):
        """Iterator to read images over time

        Generator function to read a specific image set over time. An image set is a specific row, col, field, channel, and plane.        
        
        :param self: PhenixReader object
        :param row: Well row
        :param col: Well column
        :param field: Image field of view
        :param channel: Image Channel
        :param plane: Image z-plane
        """

        well_node = self.__get_well_xml_node(row, col)

        # Get Image nodes
        image_nodes = well_node.findall("./v7:Image[@id]", self.ns)

        pattern = f"{row:02d}{col:02d}K\d+F{field}P{plane}R{channel}"

        image_id_list = []
        for image in image_nodes:
            if re.search(pattern, image.attrib['id']):
                image_id_list.append(image.attrib['id'])

        # Do we need to ensure images are properly sorted by time?
        # TODO: Also return timestamps and other metadata?

        for id in image_id_list:
            #image_node = self.__get_image_xml_node_byID(id)
            image_node = (self.__get_image_xml_node_byID(id)).find('./v7:URL', self.ns)
            image = imread((self._image_filepath / image_node.text))
            print(image_node.text)
            yield image