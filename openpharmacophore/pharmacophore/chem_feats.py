from rdkit import Chem


smarts_ligand = {
        "aromatic ring": [
            "a1aaaa1",
            "a1aaaaa1"
        ],
        "hydrophobicity": [
            '[$([S]~[#6])&!$(S~[!#6])]',
            '[C&r3]1~[C&r3]~[C&r3]1',
            '[C&r4]1~[C&r4]~[C&r4]~[C&r4]1',
            '[C&r5]1~[C&r5]~[C&r5]~[C&r5]~[C&r5]1',
            '[C&r6]1~[C&r6]~[C&r6]~[C&r6]~[C&r6]~[C&r6]1',
            '[C&r7]1~[C&r7]~[C&r7]~[C&r7]~[C&r7]~[C&r7]~[C&r7]1',
            '[C&r8]1~[C&r8]~[C&r8]~[C&r8]~[C&r8]~[C&r8]~[C&r8]~[C&r8]1',
            '[CH2X4,CH1X3,CH0X2]~[CH3X4,CH2X3,CH1X2,F,Cl,Br,I]',
            '*([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])[CH3X4,CH2X3,CH1X2,F,Cl,Br,I]',
            '[$(*([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])[CH3X4,CH2X3,CH1X2,F,Cl,Br,I])&!$(*([CH3X4,CH2X3,CH1X2,F,Cl,Br,'
            'I])([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])[CH3X4,CH2X3,CH1X2,F,Cl,Br,I])]([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])[CH3X4,'
            'CH2X3,CH1X2,F,Cl,Br,I]',
            '[$([CH2X4,CH1X3,CH0X2]~[$([!#1]);!$([CH2X4,CH1X3,CH0X2])])]~[CH2X4,CH1X3,CH0X2]~[CH2X4,CH1X3,CH0X2]',
            '[$([CH2X4,CH1X3,CH0X2]~[CH2X4,CH1X3,CH0X2]~[$([CH2X4,CH1X3,CH0X2]~[$([!#1]);!$([CH2X4,CH1X3,'
            'CH0X2])])])]~[CH2X4,CH1X3,CH0X2]~[CH2X4,CH1X3,CH0X2]~[CH2X4,CH1X3,CH0X2] ',
            '[$([CH3X4,CH2X3,CH1X2,F,Cl,Br,I])&!$(**[CH3X4,CH2X3,CH1X2,F,Cl,Br,I])]',
        ],
        "negative charge": [
            '[$([-,-2,-3])&!$(*[+,+2,+3])]',
            '[$([CX3,SX3,PX3](=O)[O-,OH])](=O)[O-,OH]',
            '[$([SX4,PX4](=O)(=O)[O-,OH])](=O)(=O)[O-,OH]',
            'c1nn[nH1]n1'
        ],
        "positive charge": [
            'N=[CX3](N)-N',
            '[$([+,+2,+3])&!$(*[-,-2,-3])]',
            '[$([CX3](=N)(-N)[!N])](=N)-N',
            '[$([NX3]([CX4])([CX4,#1])[CX4,#1])&!$([NX3]-*=[!#6])]',
        ]
    }


def feature_indices(feat_def, mol):
    """ Get the indices of the atoms that encompass a chemical
        feature.

        Parameters
        ----------
        feat_def : list[str]
            A smart features definition to find chemical features.

        mol : rdkit.Chem.Mol
            Molecule that will be scanned for the desired features.

        Returns
        -------
        list[tuple[int]]
    """
    feat_indices = []

    for smarts in feat_def:
        pattern = Chem.MolFromSmarts(smarts)
        assert pattern is not None, f"{smarts}"
        all_indices = mol.GetSubstructMatches(pattern)
        for indices in all_indices:
            feat_indices.append(indices)

    return feat_indices
