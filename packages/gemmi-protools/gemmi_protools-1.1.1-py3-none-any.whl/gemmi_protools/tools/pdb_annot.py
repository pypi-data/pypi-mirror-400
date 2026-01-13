"""
@Author: Luo Jiejian
"""
import hashlib
import os
import re
import shutil
import subprocess
import uuid
from collections import defaultdict
from importlib.resources import files

import numpy as np
from Bio import SeqIO
from anarci import run_anarci
from anarci.germlines import all_germlines

from gemmi_protools import StructureParser
from gemmi_protools.tools.align import align_sequences


def hash_sequence(seq: str) -> str:
    """Hash a sequence."""
    return hashlib.sha256(seq.encode()).hexdigest()


def get_fv_region(in_sequence: str):
    # IMGT number, include start and end
    # https://www.imgt.org/IMGTScientificChart/Nomenclature/IMGT-FRCDRdefinition.html
    # αβTCR：Light chain α, heavy chain β
    # γδTCR：Light chain γ, heavy chain δ
    imgt_scheme = dict(
        fr1=(1, 26),
        cdr1=(27, 38),
        fr2=(39, 55),
        cdr2=(56, 65),
        fr3=(66, 104),
        cdr3=(105, 117),
        fr4=(118, 128),
    )

    mapper = dict()
    num_mapper = dict()
    for k, v in imgt_scheme.items():
        for i in range(v[0], v[1] + 1):
            mapper[i] = k

            if k == "cdr1":
                ki = 1
            elif k == "cdr2":
                ki = 2
            elif k == "cdr3":
                ki = 3
            else:
                ki = 0
            num_mapper[i] = ki

    inputs = [("input", in_sequence)]
    _, numbered, alignment_details, _ = run_anarci(inputs, scheme="imgt", assign_germline=True)
    if numbered[0] is None:
        return []

    outputs = []
    for cur_numbered, cur_details in zip(numbered[0], alignment_details[0]):
        aligned_sites, start, end = cur_numbered
        if aligned_sites == []:
            continue
        # add mask
        # 9 for not Fv region
        # 0 for non-CDR region, 1, 2, 3 for CDR region for the current Fv
        mask = np.full(len(in_sequence), fill_value=9, dtype=np.int8)
        mask[start: end + 1] = 0
        i = 0
        for (site_num, _), site_aa in aligned_sites:
            if site_aa != "-":
                mask[i + start] = num_mapper[site_num]
                i += 1

        # region_seq
        regions = defaultdict(list)
        for site in aligned_sites:
            region_name = mapper[site[0][0]]
            regions[region_name].append(site[1])

        max_index = aligned_sites[-1][0][0]
        if max_index < 128:
            for idx in range(max_index + 1, 129):
                region_name = mapper[idx]
                regions[region_name].append("-")

        cdr1_seq = "".join([aa for aa in regions["cdr1"] if aa != "-"])
        cdr2_seq = "".join([aa for aa in regions["cdr2"] if aa != "-"])
        cdr3_seq = "".join([aa for aa in regions["cdr3"] if aa != "-"])

        # germ line V gene [fr1], germ line J gene [fr4]
        chain_type = cur_details["chain_type"]
        v_gene_specie, v_gene = cur_details["germlines"]["v_gene"][0]
        j_gene_specie, j_gene = cur_details["germlines"]["j_gene"][0]

        gl_fr1 = list(
            all_germlines["V"][chain_type][v_gene_specie][v_gene][imgt_scheme["fr1"][0] - 1:imgt_scheme["fr1"][1]])
        gl_fr1_mapper = dict(zip(range(imgt_scheme["fr1"][0], imgt_scheme["fr1"][1] + 1), gl_fr1))

        gl_fr4 = list(
            all_germlines["J"][chain_type][j_gene_specie][j_gene][imgt_scheme["fr4"][0] - 1:imgt_scheme["fr4"][1]])
        gl_fr4_mapper = dict(zip(range(imgt_scheme["fr4"][0], imgt_scheme["fr4"][1] + 1), gl_fr4))

        # repair the gap with gl_fr1 and gl_fr4
        # For FR1
        fixed_fr1 = []
        for site in aligned_sites:
            idx, ins = site[0]
            if imgt_scheme["fr1"][0] <= idx <= imgt_scheme["fr1"][1]:
                if ins == ' ' and site[1] == "-" and gl_fr1_mapper[idx] != "-":
                    fixed_fr1.append(gl_fr1_mapper[idx])
                else:
                    fixed_fr1.append(site[1])

        # For FR4
        fixed_fr4 = []
        for site in aligned_sites:
            idx, ins = site[0]
            if imgt_scheme["fr4"][0] <= idx <= imgt_scheme["fr4"][1]:
                if ins == ' ' and site[1] == "-" and gl_fr4_mapper[idx] != "-":
                    fixed_fr4.append(gl_fr4_mapper[idx])
                else:
                    fixed_fr4.append(site[1])

        # update regions
        regions["fr1"] = fixed_fr1
        regions["fr4"] = fixed_fr4

        fixed_fv_seq = []
        for r_name in ["fr1", "cdr1", "fr2", "cdr2", "fr3", "cdr3", "fr4"]:
            for aa in regions[r_name]:
                if aa != "-":
                    fixed_fv_seq.append(aa)
        fixed_fv_seq = "".join(fixed_fv_seq)

        outputs.append(dict(Fv_aa=fixed_fv_seq,
                            classification=v_gene[0:2],
                            chain_type=chain_type,
                            v_gene=v_gene_specie + "/" + v_gene,
                            j_gene=j_gene_specie + "/" + j_gene,
                            cdr1_aa=cdr1_seq,
                            cdr2_aa=cdr2_seq,
                            cdr3_aa=cdr3_seq,
                            mask="".join([str(i) for i in mask.tolist()])
                            )
                       )
    return outputs


def fv_region_type(inputs: list[dict]):
    n = len(inputs)
    if n == 0:
        return "not-Fv"
    elif n == 1:
        clf = inputs[0]["classification"]
        ct = inputs[0]["chain_type"]

        v = "%s%s" % (clf, ct)
        if v in ["IGH", "TRB", "TRD"]:
            return "%s/VH" % clf
        elif v in ["IGK", "IGL", "TRA", "TRG"]:
            return "%s/VL" % clf
        else:
            return "other"
    elif n == 2:
        p = {"%s%s" % (item["classification"], item["chain_type"]) for item in inputs}
        if p in [{"IGH", "IGL"}, {"IGH", "IGK"}, {"TRA", "TRB"}, {"TRG", "TRD"}]:
            clf = p.pop()[0:2]
            return "%s/scFv" % clf
        else:
            return "other"
    else:
        return "other"


def annotate_mhc(seq_dict: dict):
    """

    Args:
        seq_dict: dict,
                key: ch_id
                val: protein seq

    Returns:

    """
    hmm_model = str(files("gemmi_protools.data") / "MHC" / "MHC_combined.hmm")
    # save sequences to fasta
    # all chains of biomolecule
    home_dir = os.path.expanduser("~")
    tmp_dir = os.path.join(home_dir, str(uuid.uuid4()))
    os.makedirs(tmp_dir)

    fasta_file = os.path.join(tmp_dir, "input.fasta")
    with open(fasta_file, "w") as fo:
        for ch_id, seq in seq_dict.items():
            print(">%s" % ch_id, file=fo)
            print(seq, file=fo)

    result_file = os.path.join(tmp_dir, "result.txt")
    _path = shutil.which("hmmscan")

    if _path is None:
        raise RuntimeError("hmmscan is not found.")

    cmd = "%s --tblout %s --cut_ga %s %s" % (_path, result_file, hmm_model, fasta_file)

    try:
        _ = subprocess.run(cmd, shell=True, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as ce:
        raise Exception(ce)
    else:
        out = dict()
        with open(result_file, "r") as fi:
            for li in fi:
                if not re.match("#", li.strip()):
                    tmp = re.split(r"\s+", li.strip())[0:3]
                    out[tmp[2]] = tmp[0]
    finally:
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
    return out


def annotate_cd1(seq_dict: dict):
    ref_fa = str(files("gemmi_protools.data") / "CD1" / "CD21029_review.fasta")
    identity_thres = 0.8
    coverage_thres = 0.8

    # load reference sequences
    recorders = SeqIO.parse(ref_fa, "fasta")
    keys = ["CD1a", "CD1b", "CD1c", "CD1d", "CD1e"]

    ref_sequences = []
    ref_tags = []
    for seq in recorders:
        for k in keys:
            if k in seq.description:
                ref_tags.append(k)
                ref_sequences.append(str(seq.seq))
                break

    outputs = dict()
    for query_ch, query_seq in seq_dict.items():
        for i, target_seq in enumerate(ref_sequences):
            v = align_sequences(query_seq, target_seq)
            if v["identity"] > identity_thres and v["coverage_1"] > coverage_thres:
                # print(query_ch, v["identity"], v["coverage_1"], i)
                outputs[query_ch] = ref_tags[i]
                break
    return outputs


class ImmuneComplex(object):
    MAX_MHC_I_PEPTIDE_LEN = 13
    MAX_MHC_II_PEPTIDE_LEN = 25

    def __init__(self, struct_file: str,
                 min_fv_ppi_residues: int = 25,
                 min_cdr_ppi_residues: int = 5,
                 min_b2globulin_ppi_residues: int = 40,
                 min_mhc2ab_ppi_residues: int = 40
                 ):
        self.struct_file = struct_file
        self.min_fv_ppi_residues = min_fv_ppi_residues
        self.min_cdr_ppi_residues = min_cdr_ppi_residues
        self.min_b2globulin_ppi_residues = min_b2globulin_ppi_residues
        self.min_mhc2ab_ppi_residues = min_mhc2ab_ppi_residues

        self.st = StructureParser()
        self.st.load_from_file(struct_file)
        self.st.clean_structure(remove_ligand=False)
        self.renumber_structure(self.st)

        self.model_chains = dict()

        # Consider protein chains with non-standard residues (X) less than 0.1
        self.protein_chains = []
        self.ligand_chains = []
        self.nucl_chains = []
        self.other_polymer_chains = []
        self.pro = dict()

        for ch_id in self.st.chain_ids:
            seq = [r.name for r in self.st.get_chain(ch_id)]
            one_letter_seq = self.st.one_letter_code(seq)
            is_good = one_letter_seq.count("X") / len(one_letter_seq) < 0.1

            if ch_id in self.st.polymer_types and is_good:
                ch_type = self.st.polymer_types[ch_id]

                if ch_type.name == 'PeptideL':
                    self.protein_chains.append(ch_id)
                    self.pro[ch_id] = one_letter_seq
                elif ch_type.name in ['Dna', 'Rna']:
                    self.nucl_chains.append(ch_id)
                else:
                    self.other_polymer_chains.append(ch_id)
            else:
                self.ligand_chains.append(ch_id)

            self.model_chains[ch_id] = seq

        self.anarci_ann = self._annotate_proteins_anarci()
        self.mhc_ann = self._annotate_proteins_mhc()
        self.cd1_ann = self._annotate_proteins_cd1()

        self.ig_chains = []
        self.ig_H = []
        self.ig_L = []
        self.ig_scfv_chains = []

        self.tr_chains = []
        self.tr_H = []
        self.tr_L = []
        self.tr_scfv_chains = []

        self.other_ig_tr_chains = []

        for ch, val in self.anarci_ann.items():
            fv_type = val["fv_type"]
            if fv_type == "TR/scFv":
                self.tr_scfv_chains.append(ch)
            elif fv_type == "IG/scFv":
                self.ig_scfv_chains.append(ch)
            elif fv_type in ["TR/VH", "TR/VL"]:
                self.tr_chains.append(ch)
                if fv_type == "TR/VH":
                    self.tr_H.append(ch)
                else:
                    self.tr_L.append(ch)
            elif fv_type in ["IG/VH", "IG/VL"]:
                self.ig_chains.append(ch)
                if fv_type == "IG/VH":
                    self.ig_H.append(ch)
                else:
                    self.ig_L.append(ch)
            else:
                self.other_ig_tr_chains.append(ch)
                print("Warning: fv_type %s for chain %s: %s" % (fv_type, ch, struct_file))

        self.cd1_chains = list(self.cd1_ann.keys())

        # exclude cd1 chains with MHC annotations, due to annotation accuracy
        # CD1 annotations with higher accuracy
        self.mhc_chains = [ch for ch in self.mhc_ann.keys() if ch not in self.cd1_chains]

        self.ig_pairs = self.get_ig_pairs()
        self.tr_pairs = self.get_tr_pairs()
        self.vhh_chains = self.get_vhh()

        # peptide chains <= 25 residues
        self.peptide_chains_len = {ch: len(self.model_chains[ch]) for ch in self.protein_chains
                                   if len(self.model_chains[ch]) <= self.MAX_MHC_II_PEPTIDE_LEN}

        self.ch_types = dict()

        for ch in self.st.chain_ids:
            if ch in self.st.polymer_types:
                self.ch_types[ch] = self.st.polymer_types[ch].name
            else:
                self.ch_types[ch] = "SmallMol"

    def _annotate_proteins_anarci(self):
        outputs = dict()

        for ch, seq in self.pro.items():
            anarci_info = get_fv_region(seq)
            fv_type = fv_region_type(anarci_info)

            if fv_type != "not-Fv":
                mask = np.array([list(ann["mask"]) for ann in anarci_info], dtype="int")
                cdr_mask = np.any(np.logical_and(mask > 0, mask < 9), axis=0)
                fv_mask = np.any(np.logical_and(mask >= 0, mask < 9), axis=0)
                outputs[ch] = dict(fv_type=fv_type,
                                   cdr_mask=cdr_mask,
                                   fv_mask=fv_mask)
        return outputs

    def _annotate_proteins_mhc(self):
        if len(self.pro) > 0:
            return annotate_mhc(self.pro)
        else:
            return dict()

    def _annotate_proteins_cd1(self):
        aa_mapping = {aa: aa for aa in "ACDEFGHIKLMNPQRSTVWXY"}

        if len(self.pro) > 0:
            std_pro = {k: ''.join(aa_mapping.get(r, 'X') for r in v)
                       for k, v in self.pro.items()}
            return annotate_cd1(std_pro)
        else:
            return dict()

    @staticmethod
    def renumber_structure(struct: StructureParser):
        for chain in struct.MODEL:
            count = 1
            for residue in chain:
                residue.seqid.num = count
                residue.seqid.icode = " "
                count += 1

    def get_interface_mask(self, ch_x: str, ch_y: str):
        res_x, res_y = self.st.compute_interface([ch_x], [ch_y])
        num_x = res_x["residue_num"]
        num_y = res_y["residue_num"]

        xm = np.zeros(len(self.model_chains[ch_x]), dtype="bool")
        ym = np.zeros(len(self.model_chains[ch_y]), dtype="bool")

        xm[num_x - 1] = True
        ym[num_y - 1] = True
        return xm, ym

    def show_chains(self):
        for key in ['protein_chains', 'ligand_chains', 'nucl_chains', 'other_polymer_chains',
                    'ig_chains', 'ig_H', 'ig_L', 'ig_scfv_chains',
                    'tr_chains', 'tr_H', 'tr_L', 'tr_scfv_chains', 'mhc_chains', 'cd1_chains',
                    'ig_pairs', 'tr_pairs', "vhh_chains", "other_ig_tr_chains"
                    ]:
            print("%s: %s" % (key, str(self.__dict__[key])))

    def _hl_pairs(self, h_chains: list, l_chains: list):
        if len(h_chains) == 0 or len(l_chains) == 0:
            return []

        candidate_pairs = []
        for ch_h in h_chains:
            fv_mask_h = self.anarci_ann[ch_h]["fv_mask"]

            for ch_l in l_chains:
                fv_mask_l = self.anarci_ann[ch_l]["fv_mask"]

                ppi_h, ppi_l = self.get_interface_mask(ch_h, ch_l)
                n_ppi_h = np.logical_and(fv_mask_h, ppi_h).sum()
                n_ppi_l = np.logical_and(fv_mask_l, ppi_l).sum()

                n_ppi = n_ppi_h + n_ppi_l
                if n_ppi >= self.min_fv_ppi_residues:
                    candidate_pairs.append((ch_h, ch_l, n_ppi))
        return candidate_pairs

    def _pairs(self, chains: list):
        # For double H chains or L chains
        # anarci not always right
        chains_sort = chains.copy()
        chains_sort.sort()

        n_chains = len(chains_sort)

        if n_chains < 2:
            return []

        candidate_pairs = []
        for i in range(n_chains - 1):
            ch_i = chains_sort[i]
            fv_mask_i = self.anarci_ann[ch_i]["fv_mask"]

            for j in range(i + 1, n_chains):
                ch_j = chains_sort[j]
                fv_mask_j = self.anarci_ann[ch_j]["fv_mask"]

                ppi_i, ppi_j = self.get_interface_mask(ch_i, ch_j)
                n_ppi_i = np.logical_and(fv_mask_i, ppi_i).sum()
                n_ppi_j = np.logical_and(fv_mask_j, ppi_j).sum()

                n_ppi = n_ppi_i + n_ppi_j
                if n_ppi >= self.min_fv_ppi_residues:
                    candidate_pairs.append((ch_i, ch_j, n_ppi))
        return candidate_pairs

    def _search_pairs(self, h_chains: list, l_chains: list):
        candidate_pairs = (self._hl_pairs(h_chains=h_chains, l_chains=l_chains)
                           + self._pairs(chains=h_chains)
                           + self._pairs(chains=l_chains)
                           )
        candidate_pairs.sort(reverse=True, key=lambda x: x[2])
        # print(candidate_pairs)

        outputs = []
        _status = {ch: 0 for ch in h_chains + l_chains}

        for ch_1, ch_2, _ in candidate_pairs:
            if _status[ch_1] == 0 and _status[ch_2] == 0:
                outputs.append((ch_1, ch_2))
                _status[ch_1] = 1
                _status[ch_2] = 1
        return outputs

    def get_ig_pairs(self):
        return self._search_pairs(h_chains=self.ig_H, l_chains=self.ig_L)

    def get_tr_pairs(self):
        return self._search_pairs(h_chains=self.tr_H, l_chains=self.tr_L)

    def get_vhh(self):
        query_chains = []
        paired_chains = []
        for pair in self.ig_pairs:
            paired_chains.extend(list(pair))

        for ch in self.ig_chains:
            if ch not in paired_chains and self.anarci_ann[ch]["fv_type"] == "IG/VH":
                query_chains.append(ch)
        return query_chains

    def _search_target_chains(self, query_chains: list, query_type: str):
        """
        Not Consider IG-IG, TR-TR complexes, if exist
        """
        assert query_type in ["IG", "TR"]

        candidates = []

        if query_type == "IG":
            target_chains = list(
                set(self.st.chain_ids).difference(set(self.ig_chains + self.ig_scfv_chains + self.other_ig_tr_chains)))
        else:
            target_chains = list(
                set(self.st.chain_ids).difference(set(self.tr_chains + self.tr_scfv_chains + self.other_ig_tr_chains)))
        target_chains.sort()

        for ch_t in target_chains:

            n_cdr = 0
            for ch_q in query_chains:
                cdr_mask_q = self.anarci_ann[ch_q]["cdr_mask"]

                ppi_q, ppi_t = self.get_interface_mask(ch_q, ch_t)

                # cdr interactions
                n_cdr_q = np.logical_and(cdr_mask_q, ppi_q).sum()
                n_cdr += n_cdr_q

            if n_cdr >= self.min_cdr_ppi_residues:
                candidates.append(ch_t)
        return candidates

    def get_ig_complexes(self):
        qt = "IG"
        outputs = []
        for query in self.ig_pairs:
            tmp = self._search_target_chains(query_chains=list(query), query_type=qt)
            if tmp:
                outputs.append(dict(query_chains=list(query),
                                    target_chains=tmp,
                                    target_chains_types=[self.ch_types[ch] for ch in tmp],
                                    complex_type="IG_Ag"
                                    )
                               )
        return outputs

    def get_vhh_complexes(self):
        qt = "IG"
        pairs = [(ch,) for ch in self.vhh_chains]

        outputs = []
        for query in pairs:
            tmp = self._search_target_chains(query_chains=list(query), query_type=qt)
            if tmp:
                outputs.append(dict(query_chains=list(query),
                                    target_chains=tmp,
                                    target_chains_types=[self.ch_types[ch] for ch in tmp],
                                    complex_type="VHH_Ag"
                                    )
                               )
        return outputs

    def get_scfv_complexes(self):
        pairs = [(ch,) for ch in self.ig_scfv_chains]
        qt = "IG"

        outputs = []
        for query in pairs:
            tmp = self._search_target_chains(query_chains=list(query), query_type=qt)
            if tmp:
                outputs.append(dict(query_chains=list(query),
                                    target_chains=tmp,
                                    target_chains_types=[self.ch_types[ch] for ch in tmp],
                                    complex_type="scFv_Ag"
                                    )
                               )
        return outputs

    def find_b2mg(self, query_ch: str):
        # only right for MHC I chain or CD1 chain
        assert (query_ch in self.mhc_ann and self.mhc_ann[
            query_ch] == "MHC_I") or query_ch in self.cd1_chains, "Not MHC_I chain or CD1 chain: %s" % query_ch

        exclude_chains = (self.ig_chains
                          + self.ig_scfv_chains
                          + self.tr_chains
                          + self.tr_scfv_chains
                          + self.other_ig_tr_chains
                          + self.mhc_chains
                          + self.cd1_chains
                          )

        # not peptide chains
        candidates = []
        for cur_ch in self.protein_chains:
            seq_n = len(self.st.polymer_sequences()[cur_ch])
            if seq_n > self.MAX_MHC_II_PEPTIDE_LEN and cur_ch not in exclude_chains:
                m1, m2 = self.get_interface_mask(cur_ch, query_ch)
                n_ppi = m1.sum() + m2.sum()

                if n_ppi >= self.min_b2globulin_ppi_residues:
                    candidates.append((cur_ch, n_ppi))

        candidates.sort(reverse=True, key=lambda s: s[1])

        if len(candidates) > 0:
            return candidates[0][0]
        else:
            return ""

    def find_pair_mhc2ab(self, query_ch: str):
        if query_ch not in self.mhc_ann or self.mhc_ann[query_ch] in ["MHC_II_alpha", "MHC_II_beta"]:
            raise RuntimeError("Not MHC_II chain: %s" % query_ch)

        # query_ch must be MHC2 alpha or beta chain
        # not peptide chains
        candidates = []
        for cur_ch in self.mhc_chains:
            if cur_ch != query_ch:
                m1, _ = self.get_interface_mask(cur_ch, query_ch)
                n_ppi = m1.sum()

                if n_ppi >= self.min_mhc2ab_ppi_residues:
                    candidates.append((cur_ch, n_ppi))

        candidates.sort(reverse=True, key=lambda s: s[1])

        if len(candidates) > 0:
            return candidates[0][0]
        else:
            return ""

    def find_best_chain(self, query_chains: list, ref_chains: list):
        """
        find best chain from query_chains, which owns most interactions with ref_chains

        Return str, chain id
        """
        tmp = []
        for i, q_ch in enumerate(query_chains):

            q_masks = []
            for r_ch in ref_chains:
                qm, _ = self.get_interface_mask(q_ch, r_ch)
                q_masks.append(qm)

            n_contact_residues = np.any(np.array(q_masks), axis=0).sum()
            if n_contact_residues > 0:
                tmp.append((q_ch, n_contact_residues))

        tmp.sort(reverse=True, key=lambda s: s[1])

        if tmp:
            return tmp[0][0]
        else:
            return ""

    def _check_peptide(self, outputs: list, ligands: list, ref_type: str, ref_chains: list):
        # check peptides
        assert ref_type in ["MHC_I", "MHC_II", "CD1"]
        if ref_type in ["MHC_I", "CD1"]:
            len_threshold = self.MAX_MHC_I_PEPTIDE_LEN
        else:
            len_threshold = self.MAX_MHC_II_PEPTIDE_LEN

        query_peptides = [ch for ch, l in self.peptide_chains_len.items() if l <= len_threshold]

        if query_peptides:
            p_ch = self.find_best_chain(query_chains=query_peptides,
                                        ref_chains=ref_chains)

            # add MHC I interaction peptide chains
            if p_ch != "" and p_ch not in ligands:
                outputs += [p_ch]

    def check_mhc(self, query_chains: list, target_chains: list):
        status = defaultdict(list)
        ligand_chains = []

        for ch in target_chains:
            if ch in self.mhc_chains:
                status[self.mhc_ann[ch]].append(ch)
            else:
                ligand_chains.append(ch)

        n_status = len(status)

        complex_type = ""
        msg = ""
        output_chains = target_chains.copy()

        if n_status == 1:
            if "MHC_I" in status:
                mhc_chain = self.find_best_chain(query_chains=status["MHC_I"],
                                                 ref_chains=query_chains)

                b2 = self.find_b2mg(mhc_chain)
                # reset output_chains
                if b2 != "" and b2 not in ligand_chains:
                    output_chains = [mhc_chain, b2] + ligand_chains
                else:
                    output_chains = [mhc_chain] + ligand_chains

                self._check_peptide(outputs=output_chains,
                                    ligands=ligand_chains,
                                    ref_type="MHC_I",
                                    ref_chains=[mhc_chain])

                complex_type = "TR_MHC1"
                msg = "Success"
            elif "MHC_II_alpha" in status:
                alpha_chain = self.find_best_chain(query_chains=status["MHC_II_alpha"],
                                                   ref_chains=query_chains)

                candidate_betas = [ch for ch, t in self.mhc_ann.items() if t == "MHC_II_beta"]

                beta_chain = ""
                if candidate_betas:
                    beta_chain = self.find_best_chain(query_chains=candidate_betas, ref_chains=[alpha_chain])

                if beta_chain == "":
                    msg = "Missing MHC_II_beta chain"
                else:
                    # place MHC chains first
                    output_chains = [alpha_chain, beta_chain] + ligand_chains

                    self._check_peptide(outputs=output_chains,
                                        ligands=ligand_chains,
                                        ref_type="MHC_II",
                                        ref_chains=[alpha_chain, beta_chain])

                    msg = "Success"
                    complex_type = "TR_MHC2"

            elif "MHC_II_beta" in status:
                beta_chain = self.find_best_chain(query_chains=status["MHC_II_beta"],
                                                  ref_chains=query_chains)

                candidate_alphas = [ch for ch, t in self.mhc_ann.items() if t == "MHC_II_alpha"]

                alpha_chain = ""
                if candidate_alphas:
                    alpha_chain = self.find_best_chain(query_chains=candidate_alphas, ref_chains=[beta_chain])

                if alpha_chain == "":
                    msg = "Missing MHC_II_alpha chain"
                else:
                    output_chains = [alpha_chain, beta_chain] + ligand_chains
                    self._check_peptide(outputs=output_chains,
                                        ligands=ligand_chains,
                                        ref_type="MHC_II",
                                        ref_chains=[alpha_chain, beta_chain])
                    msg = "Success"
                    complex_type = "TR_MHC2"

        elif n_status == 2:
            if "MHC_II_alpha" in status and "MHC_II_beta" in status:
                if len(status["MHC_II_alpha"]) == 1 and len(status["MHC_II_beta"]) == 1:
                    # place MHC chains first
                    mhc_chains = [status["MHC_II_alpha"][0], status["MHC_II_beta"][0]]
                    output_chains = mhc_chains + ligand_chains

                    self._check_peptide(outputs=output_chains,
                                        ligands=ligand_chains,
                                        ref_type="MHC_II",
                                        ref_chains=mhc_chains)
                    msg = "Success"
                    complex_type = "TR_MHC2"
                else:
                    msg = "Multiple MHC_II_alpha or MHC_II_beta"
            else:
                msg = "Confusing MHC"
        elif n_status > 2:
            msg = "Confusing MHC"

        return msg, complex_type, output_chains

    def check_cd1(self, query_chains: list, target_chains: list):
        status = defaultdict(list)
        ligand_chains = []

        for ch in target_chains:
            if ch in self.cd1_chains:
                status[self.cd1_ann[ch]].append(ch)
            else:
                ligand_chains.append(ch)

        n_status = len(status)

        complex_type = ""
        msg = ""
        output_chains = target_chains.copy()

        if n_status == 1:
            cd1_type = list(status.keys())[0]

            if len(status[cd1_type]) == 1:
                cd1_chain = status[cd1_type][0]
            else:
                # multiple CD1 chains, pick the one with most interactions
                tmp = []
                for i, t_ch in enumerate(status[cd1_type]):

                    t_masks = []
                    for q_ch in query_chains:
                        tm, _ = self.get_interface_mask(t_ch, q_ch)
                        t_masks.append(tm)

                    n_contact_residues = np.any(np.array(t_masks), axis=0).sum()
                    tmp.append((t_ch, n_contact_residues))

                tmp.sort(reverse=True, key=lambda s: s[1])
                cd1_chain = tmp[0][0]

            b2 = self.find_b2mg(cd1_chain)

            # reset output_chains
            if b2 != "" and b2 not in ligand_chains:
                output_chains = [cd1_chain, b2] + ligand_chains
            else:
                output_chains = [cd1_chain] + ligand_chains

            self._check_peptide(outputs=output_chains,
                                ligands=ligand_chains,
                                ref_type="CD1",
                                ref_chains=[cd1_chain])

            complex_type = "TR_CD1"
            msg = "Success"

        elif n_status > 1:
            msg = "Multiple CD1 chains"
        return msg, complex_type, output_chains

    def get_tr_complexes(self):
        qt = "TR"
        outputs = []
        wrongs = []

        scfv_chains = [(ch,) for ch in self.tr_scfv_chains]

        for query in self.tr_pairs + scfv_chains:
            tmp = self._search_target_chains(query_chains=list(query), query_type=qt)

            if tmp:
                msg_b, complex_type_b, target_chains_b = self.check_cd1(query_chains=list(query),
                                                                        target_chains=tmp)

                msg_a, complex_type_a, target_chains_a = self.check_mhc(query_chains=list(query),
                                                                        target_chains=tmp)
                if msg_b == "Success":
                    outputs.append(dict(query_chains=list(query),
                                        target_chains=target_chains_b,
                                        target_chains_types=[self.ch_types[ch] for ch in target_chains_b],
                                        complex_type=complex_type_b
                                        )
                                   )
                elif msg_a == "Success":
                    outputs.append(dict(query_chains=list(query),
                                        target_chains=target_chains_a,
                                        target_chains_types=[self.ch_types[ch] for ch in target_chains_a],
                                        complex_type=complex_type_a
                                        )
                                   )
                elif msg_a == "" and msg_b == "":
                    # TR-Ag
                    outputs.append(dict(query_chains=list(query),
                                        target_chains=tmp,
                                        target_chains_types=[self.ch_types[ch] for ch in tmp],
                                        complex_type="TR_Ag"
                                        )
                                   )
                else:
                    wrongs.append(dict(query_chains=list(query),
                                       target_chains=tmp,
                                       target_chains_types=[self.ch_types[ch] for ch in tmp],
                                       msg_MHC=msg_a,
                                       msg_CD1=msg_b
                                       )
                                  )
        return outputs, wrongs

    def run(self):
        outputs = []
        wrongs = []
        if self.ig_pairs:
            outputs.extend(self.get_ig_complexes())
        elif self.vhh_chains:
            outputs.extend(self.get_vhh_complexes())
        elif self.ig_scfv_chains:
            outputs.extend(self.get_scfv_complexes())
        elif self.tr_pairs or self.tr_scfv_chains:
            val, wrong = self.get_tr_complexes()
            outputs.extend(val)
            wrongs.extend(wrong)
        return outputs, wrongs
