# coding=utf-8
import dragonfly.writer.model as model_writer
from .writer import model_to_dsbxml, model_to_dsbxml_file

# add writers to the honeybee-core modules
model_writer.dsbxml = model_to_dsbxml
model_writer.dsbxml_file = model_to_dsbxml_file
