# contains the default search request body from COCONUT REST API docs
# contains info for advanced molecule search like request body, tags, and filters


# citatons
default_citations_search_req = {
                                "search": {
                                           "scopes": [],
                                           "filters": [
                                                       {
                                                        "field": "doi",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "title",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "authors",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "citation_text",
                                                        "operator": "=",
                                                        "value": ""
                                                        }
                                                       ],
                                           "sorts": [
                                                     {
                                                      "field": "doi",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "title",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "authors",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "citation_text",
                                                      "direction": "desc"
                                                      }
                                                     ],
                                           "selects": [
                                                       {
                                                        "field": "doi"
                                                        },
                                                       {
                                                        "field": "title"
                                                        },
                                                       {
                                                        "field": "authors"
                                                        },
                                                       {
                                                        "field": "citation_text"
                                                        }
                                                       ],
                                           "includes": [],
                                           "aggregates": [],
                                           "instructions": [],
                                           "gates": [
                                                     "create",
                                                     "update",
                                                     "delete"
                                                     ],
                                           "page": 1,
                                           "limit": 10
                                           }
                                }


# collections
default_collections_search_req = {
                                  "search": {
                                             "scopes": [],
                                             "filters": [
                                                         {
                                                          "field": "title",
                                                          "operator": "=",
                                                          "value": ""
                                                          },
                                                         {
                                                          "field": "description",
                                                          "operator": "=",
                                                          "value": ""
                                                          },
                                                         {
                                                          "field": "identifier",
                                                          "operator": "=",
                                                          "value": ""
                                                          },
                                                         {
                                                          "field": "url",
                                                          "operator": "=",
                                                          "value": ""
                                                          }
                                                         ],
                                             "sorts": [
                                                       {
                                                        "field": "title",
                                                        "direction": "desc"
                                                        },
                                                       {
                                                        "field": "description",
                                                        "direction": "desc"
                                                        },
                                                       {
                                                        "field": "identifier",
                                                        "direction": "desc"
                                                        },
                                                       {
                                                        "field": "url",
                                                        "direction": "desc"
                                                        }
                                                       ],
                                             "selects": [
                                                         {
                                                          "field": "title"
                                                          },
                                                         {
                                                          "field": "description"
                                                          },
                                                         {
                                                          "field": "identifier"
                                                          },
                                                         {
                                                          "field": "url"
                                                          }
                                                                    ],
                                             "includes": [],
                                             "aggregates": [],
                                             "instructions": [],
                                             "gates": [
                                                       "create",
                                                       "update",
                                                       "delete"
                                                       ],
                                             "page": 1,
                                             "limit": 10
                                             }
                                  }


# molecules
default_molecules_search_req = {
                                "search": {
                                           "scopes": [],
                                           "filters": [
                                                       {
                                                        "field": "standard_inchi",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "standard_inchi_key",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "canonical_smiles",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "sugar_free_smiles",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "identifier",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "name",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "cas",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "iupac_name",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "murko_framework",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "structural_comments",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "name_trust_level",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "annotation_level",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "variants_count",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "status",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "active",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "has_variants",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "has_stereo",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "is_tautomer",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "is_parent",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "is_placeholder",
                                                        "operator": "=",
                                                        "value": ""
                                                        }
                                                       ],
                                           "sorts": [
                                                     {
                                                      "field": "standard_inchi",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "standard_inchi_key",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "canonical_smiles",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "sugar_free_smiles",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "identifier",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "name",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "cas",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "iupac_name",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "murko_framework",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "structural_comments",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "name_trust_level",
                                                      "direction": "desc"
                                                      },
                                                      {
                                                       "field": "annotation_level",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "variants_count",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "status",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "active",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "has_variants",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "has_stereo",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "is_tautomer",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "is_parent",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "is_placeholder",
                                                       "direction": "desc"
                                                       }
                                                      ],
                                           "selects": [
                                                        {
                                                         "field": "standard_inchi"
                                                         },
                                                        {
                                                         "field": "standard_inchi_key"
                                                         },
                                                        {
                                                         "field": "canonical_smiles"
                                                         },
                                                        {
                                                         "field": "sugar_free_smiles"
                                                         },
                                                        {
                                                         "field": "identifier"
                                                         },
                                                        {
                                                         "field": "name"
                                                         },
                                                        {
                                                         "field": "cas"
                                                         },
                                                        {
                                                         "field": "iupac_name"
                                                         },
                                                        {
                                                         "field": "murko_framework"
                                                         },
                                                        {
                                                         "field": "structural_comments"
                                                         },
                                                        {
                                                         "field": "name_trust_level"
                                                         },
                                                        {
                                                         "field": "annotation_level"
                                                         },
                                                        {
                                                         "field": "variants_count"
                                                         },
                                                        {
                                                         "field": "status"
                                                         },
                                                        {
                                                         "field": "active"
                                                         },
                                                        {
                                                         "field": "has_variants"
                                                         },
                                                        {
                                                         "field": "has_stereo"
                                                         },
                                                        {
                                                         "field": "is_tautomer"
                                                         },
                                                        {
                                                         "field": "is_parent"
                                                         },
                                                        {
                                                         "field": "is_placeholder"
                                                         }
                                                        ],
                                           "includes": [
                                                         {
                                                          "relation": "properties"
                                                          }
                                                         ],
                                           "aggregates": [],
                                           "instructions": [],
                                           "gates": [
                                                      "create",
                                                      "update",
                                                      "delete"
                                                      ],
                                           "page": 1,
                                           "limit": 10
                                           }
                                }


# organisms
default_organisms_search_req = {
                                "search": {
                                           "scopes": [],
                                           "filters": [
                                                       {
                                                        "field": "name",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "iri",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "rank",
                                                        "operator": "=",
                                                        "value": ""
                                                        },
                                                       {
                                                        "field": "molecule_count",
                                                        "operator": "=",
                                                        "value": ""
                                                        }
                                                       ],
                                           "sorts": [
                                                     {
                                                      "field": "name",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "iri",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "rank",
                                                      "direction": "desc"
                                                      },
                                                     {
                                                      "field": "molecule_count",
                                                      "direction": "desc"
                                                      }
                                                     ],
                                           "selects": [
                                                       {
                                                        "field": "name"
                                                        },
                                                       {
                                                        "field": "iri"
                                                        },
                                                       {
                                                        "field": "rank"
                                                        },
                                                       {
                                                        "field": "molecule_count"
                                                        }
                                                       ],
                                           "includes": [],
                                           "aggregates": [],
                                           "instructions": [],
                                           "gates": [
                                                     "create",
                                                     "update",
                                                     "delete"
                                                     ],
                                           "page": 1,
                                           "limit": 10
                                           }
                                }


# properites
default_properties_search_req = {
                                 "search": {
                                            "scopes": [],
                                            "filters": [
                                                        {
                                                         "field": "total_atom_count",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "heavy_atom_count",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "molecular_weight",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "exact_molecular_weight",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "molecular_formula",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "alogp",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "topological_polar_surface_area",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "rotatable_bond_count",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_acceptors",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_donors",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_acceptors_lipinski",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_donors_lipinski",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "lipinski_rule_of_five_violations",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "aromatic_rings_count",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "qed_drug_likeliness",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "formal_charge",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "fractioncsp3",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "number_of_minimal_rings",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "van_der_walls_volume",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "contains_sugar",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "contains_ring_sugars",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "contains_linear_sugars",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "murcko_framework",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "np_likeness",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "chemical_class",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "chemical_sub_class",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "chemical_super_class",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "direct_parent_classification",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "np_classifier_pathway",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "np_classifier_superclass",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "np_classifier_class",
                                                         "operator": "=",
                                                         "value": ""
                                                         },
                                                        {
                                                         "field": "np_classifier_is_glycoside",
                                                         "operator": "=",
                                                         "value": ""
                                                         }
                                                        ],
                                            "sorts": [
                                                      {
                                                       "field": "total_atom_count",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "heavy_atom_count",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "molecular_weight",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "exact_molecular_weight",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "molecular_formula",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "alogp",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "topological_polar_surface_area",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "rotatable_bond_count",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "hydrogen_bond_acceptors",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "hydrogen_bond_donors",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "hydrogen_bond_acceptors_lipinski",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "hydrogen_bond_donors_lipinski",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "lipinski_rule_of_five_violations",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "aromatic_rings_count",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "qed_drug_likeliness",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "formal_charge",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "fractioncsp3",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "number_of_minimal_rings",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "van_der_walls_volume",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "contains_sugar",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "contains_ring_sugars",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "contains_linear_sugars",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "murcko_framework",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "np_likeness",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "chemical_class",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "chemical_sub_class",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "chemical_super_class",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "direct_parent_classification",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "np_classifier_pathway",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "np_classifier_superclass",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "np_classifier_class",
                                                       "direction": "desc"
                                                       },
                                                      {
                                                       "field": "np_classifier_is_glycoside",
                                                       "direction": "desc"
                                                       }
                                                      ],        
                                            "selects": [
                                                        {
                                                         "field": "total_atom_count"
                                                         },
                                                        {
                                                         "field": "heavy_atom_count"
                                                         },
                                                        {
                                                         "field": "molecular_weight"
                                                         },
                                                        {
                                                         "field": "exact_molecular_weight"
                                                         },
                                                        {
                                                         "field": "molecular_formula"
                                                         },
                                                        {
                                                         "field": "alogp"
                                                         },
                                                        {
                                                         "field": "topological_polar_surface_area"
                                                         },
                                                        {
                                                         "field": "rotatable_bond_count"
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_acceptors"
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_donors"
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_acceptors_lipinski"
                                                         },
                                                        {
                                                         "field": "hydrogen_bond_donors_lipinski"
                                                         },
                                                        {
                                                         "field": "lipinski_rule_of_five_violations"
                                                         },
                                                        {
                                                         "field": "aromatic_rings_count"
                                                         },
                                                        {
                                                         "field": "qed_drug_likeliness"
                                                         },
                                                        {
                                                         "field": "formal_charge"
                                                         },
                                                        {
                                                         "field": "fractioncsp3"
                                                         },
                                                        {
                                                         "field": "number_of_minimal_rings"
                                                         },
                                                        {
                                                         "field": "van_der_walls_volume"
                                                         },
                                                        {
                                                         "field": "contains_sugar"
                                                         },
                                                        {
                                                         "field": "contains_ring_sugars"
                                                         },
                                                        {
                                                         "field": "contains_linear_sugars"
                                                         },
                                                        {
                                                         "field": "murcko_framework"
                                                         },
                                                        {
                                                         "field": "np_likeness"
                                                         },
                                                        {
                                                         "field": "chemical_class"
                                                         },
                                                        {
                                                         "field": "chemical_sub_class"
                                                         },
                                                        {
                                                         "field": "chemical_super_class"
                                                         },
                                                        {
                                                         "field": "direct_parent_classification"
                                                         },
                                                        {
                                                         "field": "np_classifier_pathway"
                                                         },
                                                        {
                                                         "field": "np_classifier_superclass"
                                                         },
                                                        {
                                                         "field": "np_classifier_class"
                                                         },
                                                        {
                                                         "field": "np_classifier_is_glycoside"
                                                         }
                                                        ],
                                            "includes": [
                                                         {
                                                          "relation": "molecule"
                                                          }
                                                         ],
                                            "aggregates": [],
                                            "instructions": [],
                                            "gates": [
                                                      "create",
                                                      "update",
                                                      "delete"
                                                      ],
                                            "page": 1,
                                            "limit": 10
                                            }
                                 }


# reports
default_reports_search_req = {
                              "search": {
                                         "scopes": [],
                                         "filters": [
                                                     {
                                                      "field": "title",
                                                      "operator": "=",
                                                      "value": ""
                                                      },
                                                     {
                                                      "field": "evidence",
                                                      "operator": "=",
                                                      "value": ""
                                                      },
                                                     {
                                                      "field": "comment",
                                                      "operator": "=",
                                                      "value": ""
                                                      },
                                                     {
                                                      "field": "suggested_changes",
                                                      "operator": "=",
                                                      "value": ""
                                                      }
                                                     ],
                                         "sorts": [
                                                   {
                                                    "field": "title",
                                                    "direction": "desc"
                                                    },
                                                   {
                                                    "field": "evidence",
                                                    "direction": "desc"
                                                    },
                                                   {
                                                    "field": "comment",
                                                    "direction": "desc"
                                                    }
                                                   ],
                                         "selects": [
                                                     {
                                                      "field": "title"
                                                      },
                                                     {
                                                      "field": "evidence"
                                                      },
                                                     {
                                                      "field": "comment"
                                                      },
                                                     {
                                                      "field": "suggested_changes"
                                                      }
                                                     ],
                                         "includes": [],
                                         "aggregates": [],
                                         "instructions": [],
                                         "gates": [
                                                   "create",
                                                   "update",
                                                   "delete"
                                                   ],
                                         "page": 1,
                                         "limit": 10
                                         }
                              }         


# advanced molecule search info
adv_mol_search_info = {
                       "search" : {
                                   "type" : "",
                                   "tagType" : "",
                                   "query" : "",
                                   "limit" : "",
                                   "sort" : "",
                                   "page" : "",
                                   "offset" : ""
                                   },
                       "tags" : [
                                 "dataSource",
                                 "organisms",
                                 "citations"
                                 ],
                       "filters" : [
                                    # Molecular properties
                                    "tac", "hac", "mw", "emw", "mrc", "vdwv", "fc",
                                    # Chemical properties
                                    "alogp", "topopsa", "fcsp3", "np", "qed",
                                    # Structural features
                                    "rbc", "arc", "hba", "hbd",
                                    # Lipinski parameters
                                    "lhba", "lhbd", "lro5v",
                                    # Sugar-related
                                    "cs", "crs", "cls",
                                    # Classyfire classifications
                                    "class", "subclass", "superclass", "parent",
                                    # NP classifier
                                    "np_pathway", "np_superclass", "np_class", "np_glycoside"
                                    ]
                       }
