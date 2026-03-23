"""
Sample Company Data
Pre-loaded with actual financial data from real public company 10-K filings.
Two companies per industry (one strong performer, one weak) across varied sizes.
Data sourced from FY2023 and FY2022 SEC 10-K annual reports.
"""


def _co(industry, current, prior, dcf, current_year="2023", prior_year="2022"):
    """Shorthand builder for a sample company entry."""
    return {"industry": industry, "current": current, "prior": prior, "dcf_defaults": dcf,
            "current_year": current_year, "prior_year": prior_year}


def _bs(ca, cl, ta, tl, te, cash, inv, ar, ap, ltd, re, mcap, ppe=0, intang=0, shares=100_000_000):
    """Balance sheet helper."""
    return dict(
        total_current_assets=ca, total_current_liabilities=cl,
        total_assets=ta, total_liabilities=tl, total_equity=te,
        cash=cash, inventory=inv, accounts_receivable=ar, accounts_payable=ap,
        long_term_debt=ltd, retained_earnings=re, market_cap=mcap,
        ppe_net=ppe, intangibles=intang, shares_outstanding=shares,
    )


def _is_(rev, cogs, opex, oi, intexp, tax, ni, dep, sga=0):
    """Income statement helper."""
    return dict(
        revenue=rev, cogs=cogs, operating_expenses=opex,
        operating_income=oi, ebit=oi, interest_expense=intexp,
        tax_expense=tax, net_income=ni, depreciation=dep, sga_expense=sga,
    )


def _cf(ocf, capex):
    """Cash flow helper."""
    return dict(operating_cash_flow=ocf, capital_expenditures=capex)


def _year(bs, is_, cf):
    """Merge BS + IS + CF into one dict."""
    d = {}
    d.update(bs)
    d.update(is_)
    d.update(cf)
    return d


def _dcf(gr, em, capex_pct, nwc, da, rfr, erp, beta, cod, tax, eq_w, tgr, shares, nd):
    return dict(
        revenue_growth_rates=gr, ebitda_margins=em, capex_pct=capex_pct,
        nwc_change_pct=nwc, da_pct=da, risk_free_rate=rfr,
        equity_risk_premium=erp, beta=beta, cost_of_debt=cod,
        tax_rate=tax, equity_weight=eq_w, debt_weight=round(1 - eq_w, 2),
        terminal_growth_rate=tgr, shares_outstanding=shares, net_debt=nd,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE COMPANIES — Real public companies with actual 10-K data (FY2023/FY2022)
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_COMPANIES = {

    # ── Technology / SaaS ────────────────────────────────────────────────────

    # ADBE - Adobe Inc. — Large-Cap, high-margin SaaS (FY ends Nov)
    "ADBE - Adobe (Strong SaaS)": _co("Technology / SaaS",
        _year(  # FY2023 (ended Dec 1, 2023)
            _bs(8_943e6, 7_402e6, 29_779e6, 15_185e6, 14_594e6, 7_141e6, 0, 2_224e6, 573e6, 3_634e6, 3_745e6, 272_000e6, 1_411e6, 12_875e6, 456e6),
            _is_(19_409e6, 3_498e6, 6_462e6, 6_690e6, 153e6, 1_424e6, 5_407e6, 1_093e6, 6_462e6),
            _cf(7_302e6, 536e6),
        ),
        _year(  # FY2022 (ended Dec 2, 2022)
            _bs(7_202e6, 7_117e6, 27_241e6, 14_473e6, 12_768e6, 5_760e6, 0, 1_850e6, 506e6, 3_628e6, 824e6, 160_000e6, 1_329e6, 12_706e6, 464e6),
            _is_(17_606e6, 3_167e6, 5_850e6, 6_100e6, 162e6, 1_252e6, 4_756e6, 1_014e6, 5_850e6),
            _cf(7_838e6, 530e6),
        ),
        _dcf([.11,.10,.09,.08,.07], [.38,.39,.40,.41,.42], .03, .08, .056,
             .043, .055, 1.05, .04, .21, .90, .025, 456e6, -3_507e6),
    ),

    # SNAP - Snap Inc. — Mid-Cap, unprofitable social media
    "SNAP - Snap (Weak Tech)": _co("Technology / SaaS",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(4_382e6, 1_598e6, 7_303e6, 4_413e6, 2_890e6, 3_200e6, 0, 920e6, 310e6, 1_800e6, -7_469e6, 18_000e6, 655e6, 1_970e6, 734e6),
            _is_(4_606e6, 2_059e6, 2_270e6, -1_378e6, 92e6, 21e6, -1_325e6, 280e6, 2_270e6),
            _cf(-171e6, 75e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(5_683e6, 1_546e6, 8_390e6, 4_717e6, 3_673e6, 4_200e6, 0, 800e6, 280e6, 1_750e6, -6_144e6, 16_000e6, 610e6, 2_100e6, 660e6),
            _is_(4_602e6, 2_143e6, 2_355e6, -1_475e6, 78e6, 9e6, -1_430e6, 255e6, 2_355e6),
            _cf(-124e6, 65e6),
        ),
        _dcf([.08,.10,.12,.10,.08], [.02,.05,.08,.10,.12], .02, .10, .061,
             .043, .055, 1.8, .08, .21, .70, .03, 734e6, -1_400e6),
    ),

    # ── Manufacturing ────────────────────────────────────────────────────────

    # CAT - Caterpillar Inc. — Large-Cap, dominant equipment maker
    "CAT - Caterpillar (Strong Manufacturer)": _co("Manufacturing",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(32_315e6, 24_766e6, 87_476e6, 65_643e6, 21_833e6, 7_011e6, 16_565e6, 9_383e6, 6_581e6, 24_473e6, 23_413e6, 150_000e6, 11_702e6, 3_200e6, 497e6),
            _is_(67_060e6, 44_249e6, 8_200e6, 12_757e6, 832e6, 2_817e6, 10_335e6, 2_966e6, 8_200e6),
            _cf(12_852e6, 2_697e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(31_631e6, 25_632e6, 82_793e6, 64_634e6, 18_159e6, 6_004e6, 16_270e6, 8_845e6, 6_289e6, 25_714e6, 20_848e6, 128_000e6, 10_818e6, 3_100e6, 521e6),
            _is_(59_427e6, 39_530e6, 7_500e6, 10_167e6, 856e6, 2_063e6, 6_705e6, 2_754e6, 7_500e6),
            _cf(9_254e6, 2_406e6),
        ),
        _dcf([.05,.04,.04,.03,.03], [.24,.24,.25,.25,.25], .04, .06, .044,
             .043, .055, 1.05, .05, .21, .75, .025, 497e6, 17_462e6),
    ),

    # NWL - Newell Brands — Mid-Cap, struggling consumer/industrial
    "NWL - Newell Brands (Weak Manufacturer)": _co("Manufacturing",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(2_614e6, 2_640e6, 12_253e6, 8_991e6, 3_262e6, 371e6, 1_270e6, 849e6, 832e6, 4_417e6, -4_300e6, 3_700e6, 1_145e6, 6_456e6, 416e6),
            _is_(8_134e6, 5_650e6, 1_949e6, -389e6, 340e6, -69e6, -511e6, 371e6, 1_949e6),
            _cf(619e6, 182e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(3_254e6, 3_202e6, 14_108e6, 10_205e6, 3_903e6, 330e6, 1_810e6, 942e6, 965e6, 4_805e6, -2_500e6, 6_300e6, 1_210e6, 7_860e6, 415e6),
            _is_(9_459e6, 6_467e6, 2_100e6, 102e6, 353e6, 36e6, -2_646e6, 398e6, 2_100e6),
            _cf(521e6, 199e6),
        ),
        _dcf([-.05,-.02,.01,.02,.03], [.06,.08,.10,.11,.12], .02, .08, .046,
             .043, .055, 1.5, .07, .21, .45, .02, 416e6, 4_046e6),
    ),

    # ── Retail ───────────────────────────────────────────────────────────────

    # COST - Costco Wholesale — Mega-Cap, dominant warehouse club
    "COST - Costco (Strong Retailer)": _co("Retail",
        _year(  # FY2023 (ended Sep 3, 2023)
            _bs(28_180e6, 28_929e6, 64_166e6, 43_518e6, 20_648e6, 13_700e6, 16_651e6, 2_285e6, 17_483e6, 6_420e6, 13_040e6, 252_000e6, 24_813e6, 1_021e6, 443e6),
            _is_(242_290e6, 210_955e6, 14_814e6, 8_861e6, 343e6, 2_195e6, 6_292e6, 2_077e6, 14_814e6),
            _cf(11_068e6, 4_323e6),
        ),
        _year(  # FY2022 (ended Aug 28, 2022)
            _bs(26_580e6, 27_830e6, 59_268e6, 40_725e6, 18_543e6, 10_203e6, 15_540e6, 2_241e6, 17_816e6, 6_472e6, 11_667e6, 222_000e6, 23_329e6, 942e6, 443e6),
            _is_(226_954e6, 197_550e6, 13_820e6, 8_096e6, 158e6, 2_081e6, 5_844e6, 1_900e6, 13_820e6),
            _cf(7_392e6, 3_891e6),
        ),
        _dcf([.07,.06,.05,.05,.04], [.045,.046,.047,.048,.048], .018, .05, .009,
             .043, .055, 0.75, .03, .21, .90, .025, 443e6, -7_280e6),
    ),

    # M - Macy's Inc. — Mid-Cap, struggling department store
    "M - Macy's (Weak Retailer)": _co("Retail",
        _year(  # FY2023 (ended Feb 3, 2024)
            _bs(6_297e6, 5_468e6, 16_284e6, 13_268e6, 3_016e6, 1_034e6, 3_464e6, 388e6, 1_570e6, 2_998e6, 5_569e6, 5_400e6, 4_498e6, 3_250e6, 271e6),
            _is_(23_092e6, 14_237e6, 5_125e6, 1_204e6, 178e6, 185e6, 105e6, 966e6, 5_125e6),
            _cf(1_432e6, 786e6),
        ),
        _year(  # FY2022 (ended Jan 28, 2023)
            _bs(6_923e6, 5_692e6, 16_866e6, 13_447e6, 3_419e6, 862e6, 3_969e6, 375e6, 1_824e6, 3_248e6, 5_930e6, 5_400e6, 4_686e6, 3_265e6, 273e6),
            _is_(24_442e6, 15_164e6, 4_974e6, 1_643e6, 179e6, 362e6, 1_177e6, 961e6, 4_974e6),
            _cf(1_627e6, 845e6),
        ),
        _dcf([-.03,-.02,.00,.01,.02], [.07,.07,.08,.08,.09], .034, .06, .042,
             .043, .055, 1.3, .07, .21, .45, .02, 271e6, 1_964e6),
    ),

    # ── Healthcare ───────────────────────────────────────────────────────────

    # ABT - Abbott Laboratories — Large-Cap, diversified med-tech
    "ABT - Abbott Labs (Strong Healthcare)": _co("Healthcare",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(19_240e6, 12_534e6, 68_154e6, 34_587e6, 33_567e6, 6_888e6, 5_221e6, 5_129e6, 3_988e6, 13_599e6, 46_895e6, 190_500e6, 9_249e6, 30_370e6, 1_730e6),
            _is_(40_109e6, 20_042e6, 7_523e6, 7_790e6, 585e6, 1_230e6, 7_241e6, 2_754e6, 7_523e6),
            _cf(8_471e6, 1_898e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(21_043e6, 13_600e6, 67_837e6, 35_290e6, 32_547e6, 8_787e6, 5_529e6, 5_271e6, 4_442e6, 14_537e6, 43_619e6, 175_000e6, 8_781e6, 30_190e6, 1_740e6),
            _is_(43_653e6, 19_797e6, 8_258e6, 10_845e6, 475e6, 1_812e6, 9_282e6, 2_639e6, 8_258e6),
            _cf(8_827e6, 2_004e6),
        ),
        _dcf([.04,.04,.05,.05,.04], [.26,.27,.27,.28,.28], .047, .07, .069,
             .043, .055, 0.90, .04, .21, .75, .025, 1_730e6, 6_711e6),
    ),

    # TDOC - Teladoc Health — Mid-Cap, money-losing telehealth
    "TDOC - Teladoc (Weak Healthcare)": _co("Healthcare",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(1_567e6, 750e6, 14_754e6, 2_575e6, 12_179e6, 977e6, 0, 371e6, 74e6, 1_564e6, -16_697e6, 3_400e6, 133e6, 12_520e6, 165e6),
            _is_(2_600e6, 1_573e6, 1_724e6, -697e6, 68e6, -34e6, -782e6, 590e6, 1_724e6),
            _cf(406e6, 208e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(1_571e6, 716e6, 15_390e6, 2_505e6, 12_885e6, 893e6, 0, 451e6, 85e6, 1_547e6, -15_915e6, 3_800e6, 142e6, 13_142e6, 163e6),
            _is_(2_406e6, 1_517e6, 14_295e6, -13_406e6, 57e6, -116e6, -13_663e6, 592e6, 14_295e6),
            _cf(253e6, 261e6),
        ),
        _dcf([.08,.10,.12,.10,.08], [.02,.05,.08,.10,.12], .08, .10, .227,
             .043, .055, 1.8, .08, .21, .85, .03, 165e6, 587e6),
    ),

    # ── Financial Services ───────────────────────────────────────────────────

    # V - Visa Inc. — Mega-Cap, dominant payment network (FY ends Sep)
    "V - Visa (Strong Financial)": _co("Financial Services",
        _year(  # FY2023 (ended Sep 30, 2023)
            _bs(20_013e6, 16_644e6, 90_499e6, 54_710e6, 35_789e6, 16_286e6, 0, 1_776e6, 418e6, 20_463e6, 19_429e6, 498_000e6, 3_138e6, 29_651e6, 2_034e6),
            _is_(32_653e6, 6_368e6, 3_270e6, 20_526e6, 642e6, 3_765e6, 17_273e6, 1_082e6, 3_270e6),
            _cf(19_695e6, 1_137e6),
        ),
        _year(  # FY2022 (ended Sep 30, 2022)
            _bs(20_096e6, 16_273e6, 85_501e6, 49_939e6, 35_562e6, 15_689e6, 0, 1_866e6, 352e6, 20_200e6, 16_116e6, 379_000e6, 2_809e6, 27_802e6, 2_083e6),
            _is_(29_310e6, 5_765e6, 2_776e6, 18_814e6, 538e6, 3_191e6, 14_957e6, 862e6, 2_776e6),
            _cf(17_889e6, 870e6),
        ),
        _dcf([.10,.09,.08,.07,.06], [.66,.67,.67,.68,.68], .035, .04, .033,
             .043, .055, 0.95, .04, .21, .85, .025, 2_034e6, 4_177e6),
    ),

    # NYCB - NY Community Bancorp — Mid-Cap, troubled bank
    "NYCB - NY Community Bancorp (Weak Financial)": _co("Financial Services",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(7_258e6, 4_555e6, 114_178e6, 104_700e6, 9_478e6, 7_258e6, 0, 150e6, 80e6, 17_440e6, 3_127e6, 6_900e6, 1_067e6, 3_465e6, 719e6),
            _is_(4_211e6, 2_789e6, 1_600e6, 1_422e6, 4_555e6, -93e6, -260e6, 191e6, 1_600e6),
            _cf(1_180e6, 220e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(4_218e6, 877e6, 90_106e6, 82_100e6, 8_006e6, 4_218e6, 0, 140e6, 75e6, 13_590e6, 3_565e6, 6_800e6, 760e6, 2_431e6, 707e6),
            _is_(2_942e6, 1_445e6, 900e6, 1_497e6, 877e6, 247e6, 904e6, 86e6, 900e6),
            _cf(1_345e6, 95e6),
        ),
        _dcf([.02,.02,.03,.03,.03], [.20,.21,.22,.22,.23], .002, .05, .045,
             .043, .055, 1.3, .06, .21, .25, .02, 719e6, 10_182e6),
    ),

    # ── Energy ───────────────────────────────────────────────────────────────

    # CVX - Chevron Corporation — Mega-Cap, integrated oil major
    "CVX - Chevron (Strong Energy)": _co("Energy",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(29_838e6, 28_748e6, 261_632e6, 107_910e6, 152_638e6, 8_178e6, 5_969e6, 12_965e6, 13_057e6, 20_307e6, 177_132e6, 288_000e6, 151_555e6, 4_720e6, 1_924e6),
            _is_(196_913e6, 153_741e6, 16_249e6, 26_356e6, 567e6, 8_028e6, 21_369e6, 19_363e6, 16_249e6),
            _cf(35_616e6, 15_829e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(35_073e6, 34_057e6, 257_709e6, 107_055e6, 149_586e6, 17_678e6, 6_562e6, 14_891e6, 17_081e6, 21_375e6, 167_067e6, 339_000e6, 142_036e6, 4_592e6, 1_957e6),
            _is_(246_252e6, 195_530e6, 14_321e6, 41_801e6, 516e6, 14_066e6, 35_465e6, 17_458e6, 14_321e6),
            _cf(49_602e6, 11_975e6),
        ),
        _dcf([-.02,.01,.02,.02,.02], [.23,.23,.22,.22,.22], .06, .05, .099,
             .043, .055, 1.0, .04, .21, .75, .02, 1_924e6, 12_129e6),
    ),

    # RIG - Transocean Ltd. — Mid-Cap, debt-laden offshore driller
    "RIG - Transocean (Weak Energy)": _co("Energy",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(2_782e6, 1_404e6, 20_835e6, 12_658e6, 8_177e6, 706e6, 371e6, 660e6, 264e6, 7_227e6, -8_476e6, 4_800e6, 17_178e6, 210e6, 757e6),
            _is_(3_083e6, 1_863e6, 903e6, -655e6, 576e6, 41e6, -954e6, 672e6, 903e6),
            _cf(302e6, 245e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(3_048e6, 1_223e6, 21_181e6, 12_521e6, 8_660e6, 1_340e6, 374e6, 521e6, 239e6, 6_940e6, -7_522e6, 3_100e6, 17_435e6, 260e6, 700e6),
            _is_(2_582e6, 1_734e6, 738e6, -890e6, 588e6, 79e6, -621e6, 672e6, 738e6),
            _cf(-190e6, 164e6),
        ),
        _dcf([.10,.08,.06,.05,.04], [.12,.15,.18,.20,.22], .08, .06, .218,
             .043, .055, 1.7, .09, .21, .40, .02, 757e6, 6_521e6),
    ),

    # ── Real Estate ──────────────────────────────────────────────────────────

    # PLD - Prologis Inc. — Mega-Cap, dominant logistics REIT
    "PLD - Prologis (Strong REIT)": _co("Real Estate",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(3_023e6, 4_319e6, 93_632e6, 42_447e6, 47_460e6, 503e6, 0, 489e6, 578e6, 27_552e6, 5_700e6, 121_000e6, 68_261e6, 3_500e6, 918e6),
            _is_(8_019e6, 2_098e6, 1_459e6, 4_462e6, 644e6, 107e6, 3_068e6, 2_765e6, 1_459e6),
            _cf(5_806e6, 4_267e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(3_584e6, 3_949e6, 92_346e6, 40_218e6, 48_432e6, 542e6, 0, 399e6, 655e6, 26_169e6, 6_200e6, 108_000e6, 67_394e6, 3_600e6, 911e6),
            _is_(6_903e6, 1_679e6, 992e6, 6_232e6, 421e6, 112e6, 4_795e6, 2_209e6, 992e6),
            _cf(5_200e6, 7_156e6),
        ),
        _dcf([.08,.06,.05,.04,.04], [.56,.57,.58,.59,.60], .053, .03, .345,
             .043, .055, 0.80, .04, .21, .50, .025, 918e6, 27_049e6),
    ),

    # VNO - Vornado Realty Trust — Mid-Cap, struggling office REIT
    "VNO - Vornado Realty (Weak REIT)": _co("Real Estate",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(1_510e6, 1_125e6, 16_127e6, 11_700e6, 3_427e6, 913e6, 0, 98e6, 115e6, 8_289e6, -5_200e6, 5_200e6, 12_100e6, 1_100e6, 191e6),
            _is_(1_708e6, 954e6, 377e6, -282e6, 358e6, 4e6, -318e6, 459e6, 377e6),
            _cf(453e6, 170e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(1_450e6, 940e6, 16_414e6, 11_308e6, 4_012e6, 648e6, 0, 91e6, 108e6, 8_150e6, -4_980e6, 4_900e6, 12_550e6, 1_200e6, 192e6),
            _is_(1_708e6, 916e6, 253e6, 93e6, 299e6, 5e6, -154e6, 446e6, 253e6),
            _cf(527e6, 271e6),
        ),
        _dcf([-.02,.00,.01,.02,.02], [.26,.28,.30,.32,.34], .01, .04, .269,
             .043, .055, 1.2, .06, .21, .35, .02, 191e6, 7_376e6),
    ),

    # ── Consumer Goods ───────────────────────────────────────────────────────

    # PG - Procter & Gamble — Mega-Cap, global brand powerhouse (FY ends Jun)
    "PG - Procter & Gamble (Strong CPG)": _co("Consumer Goods",
        _year(  # FY2023 (ended Jun 30, 2023)
            _bs(22_648e6, 33_081e6, 120_829e6, 73_909e6, 46_085e6, 8_246e6, 6_581e6, 4_955e6, 13_702e6, 24_378e6, 103_829e6, 358_000e6, 21_806e6, 55_259e6, 2_359e6),
            _is_(82_006e6, 42_957e6, 20_915e6, 18_134e6, 756e6, 3_615e6, 14_653e6, 3_121e6, 20_915e6),
            _cf(16_848e6, 3_586e6),
        ),
        _year(  # FY2022 (ended Jun 30, 2022)
            _bs(21_653e6, 33_081e6, 117_208e6, 71_087e6, 45_272e6, 7_214e6, 7_275e6, 4_832e6, 14_430e6, 22_880e6, 99_420e6, 338_000e6, 21_280e6, 53_717e6, 2_401e6),
            _is_(80_187e6, 43_841e6, 19_338e6, 17_008e6, 439e6, 3_202e6, 14_742e6, 2_893e6, 19_338e6),
            _cf(16_723e6, 3_159e6),
        ),
        _dcf([.03,.03,.03,.03,.03], [.26,.27,.27,.28,.28], .044, .05, .038,
             .043, .055, 0.60, .03, .21, .80, .025, 2_359e6, 16_132e6),
    ),

    # KHC - Kraft Heinz Co. — Large-Cap, high debt, brand erosion
    "KHC - Kraft Heinz (Weak CPG)": _co("Consumer Goods",
        _year(  # FY2023 (ended Dec 30, 2023)
            _bs(8_834e6, 8_679e6, 87_803e6, 51_858e6, 35_945e6, 1_400e6, 3_605e6, 2_078e6, 4_654e6, 19_394e6, -25_820e6, 44_600e6, 7_122e6, 62_872e6, 1_218e6),
            _is_(26_065e6, 17_270e6, 3_739e6, 4_861e6, 1_033e6, 826e6, 2_843e6, 1_195e6, 3_739e6),
            _cf(4_481e6, 882e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(9_161e6, 9_774e6, 90_628e6, 55_267e6, 35_361e6, 1_040e6, 3_869e6, 2_261e6, 5_024e6, 20_088e6, -28_211e6, 49_200e6, 7_168e6, 65_453e6, 1_225e6),
            _is_(26_485e6, 18_291e6, 2_720e6, 5_474e6, 1_053e6, 701e6, 2_363e6, 1_174e6, 2_720e6),
            _cf(3_786e6, 945e6),
        ),
        _dcf([-.01,.00,.01,.01,.02], [.23,.23,.24,.24,.25], .034, .06, .046,
             .043, .055, 0.80, .05, .21, .65, .02, 1_218e6, 17_994e6),
    ),

    # ── Telecommunications ───────────────────────────────────────────────────

    # TMUS - T-Mobile US — Large-Cap, post-Sprint growth
    "TMUS - T-Mobile (Strong Telecom)": _co("Telecommunications",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(23_719e6, 22_100e6, 207_682e6, 139_670e6, 68_012e6, 5_135e6, 1_524e6, 6_497e6, 6_354e6, 65_490e6, 2_949e6, 191_000e6, 40_590e6, 86_008e6, 1_175e6),
            _is_(78_559e6, 37_684e6, 12_321e6, 14_337e6, 3_416e6, 2_605e6, 8_317e6, 14_217e6, 12_321e6),
            _cf(18_559e6, 9_239e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(22_063e6, 21_637e6, 210_742e6, 147_067e6, 63_675e6, 4_848e6, 1_773e6, 5_570e6, 7_492e6, 67_312e6, -5_368e6, 145_000e6, 42_309e6, 87_764e6, 1_237e6),
            _is_(79_571e6, 40_220e6, 14_526e6, 10_608e6, 3_364e6, 770e6, 2_590e6, 14_848e6, 14_526e6),
            _cf(16_781e6, 9_875e6),
        ),
        _dcf([.04,.04,.03,.03,.03], [.36,.37,.38,.38,.39], .118, .04, .181,
             .043, .055, 0.90, .05, .21, .55, .025, 1_175e6, 60_355e6),
    ),

    # LUMN - Lumen Technologies — Mid-Cap, declining legacy telecom
    "LUMN - Lumen Technologies (Weak Telecom)": _co("Telecommunications",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(3_866e6, 4_997e6, 29_180e6, 28_587e6, 593e6, 1_425e6, 194e6, 1_559e6, 1_495e6, 18_573e6, -19_455e6, 1_670e6, 13_968e6, 6_700e6, 1_010e6),
            _is_(14_059e6, 7_760e6, 9_182e6, -8_883e6, 1_531e6, -1_741e6, -12_242e6, 3_141e6, 9_182e6),
            _cf(2_877e6, 2_935e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(5_050e6, 5_139e6, 41_538e6, 35_032e6, 6_506e6, 615e6, 216e6, 1_855e6, 1_684e6, 20_282e6, -7_213e6, 5_260e6, 18_143e6, 12_872e6, 1_002e6),
            _is_(17_478e6, 9_469e6, 6_510e6, -1_499e6, 1_396e6, -398e6, -1_554e6, 3_521e6, 6_510e6),
            _cf(4_346e6, 3_122e6),
        ),
        _dcf([-.08,-.05,-.03,.00,.01], [.20,.22,.24,.25,.26], .21, .05, .223,
             .043, .055, 1.5, .08, .21, .25, .015, 1_010e6, 17_148e6),
    ),

    # ── Utilities ────────────────────────────────────────────────────────────

    # NEE - NextEra Energy — Large-Cap, renewable energy leader
    "NEE - NextEra Energy (Strong Utility)": _co("Utilities",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(12_893e6, 20_978e6, 168_088e6, 118_700e6, 49_388e6, 2_293e6, 1_456e6, 4_102e6, 3_670e6, 58_289e6, 15_740e6, 124_900e6, 79_206e6, 6_348e6, 2_052e6),
            _is_(28_114e6, 19_310e6, 3_021e6, 5_783e6, 3_821e6, -741e6, 7_310e6, 5_476e6, 3_021e6),
            _cf(10_904e6, 17_311e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(11_012e6, 18_749e6, 147_639e6, 104_234e6, 43_405e6, 1_693e6, 1_347e6, 3_718e6, 3_396e6, 49_771e6, 11_877e6, 167_600e6, 67_419e6, 6_378e6, 1_981e6),
            _is_(20_956e6, 12_994e6, 2_478e6, 5_484e6, 2_566e6, -367e6, 4_147e6, 4_477e6, 2_478e6),
            _cf(8_404e6, 14_952e6),
        ),
        _dcf([.08,.07,.06,.05,.04], [.40,.40,.41,.41,.42], .62, .03, .195,
             .043, .055, 0.65, .04, .21, .55, .025, 2_052e6, 55_996e6),
    ),

    # PCG - PG&E Corp. — Large-Cap, post-bankruptcy utility
    "PCG - PG&E Corp. (Weak Utility)": _co("Utilities",
        _year(  # FY2023 (ended Dec 31, 2023)
            _bs(7_835e6, 12_689e6, 113_197e6, 87_577e6, 25_620e6, 768e6, 561e6, 2_478e6, 2_564e6, 38_411e6, -2_693e6, 36_500e6, 58_949e6, 6_735e6, 2_135e6),
            _is_(24_428e6, 14_714e6, 5_043e6, 4_671e6, 2_353e6, 246e6, 2_242e6, 4_452e6, 5_043e6),
            _cf(7_118e6, 8_503e6),
        ),
        _year(  # FY2022 (ended Dec 31, 2022)
            _bs(8_419e6, 12_233e6, 107_460e6, 84_140e6, 23_320e6, 623e6, 543e6, 2_381e6, 2_539e6, 36_510e6, -4_935e6, 31_300e6, 53_048e6, 6_750e6, 2_082e6),
            _is_(21_680e6, 12_497e6, 4_867e6, 4_316e6, 2_051e6, 275e6, 1_802e6, 3_977e6, 4_867e6),
            _cf(5_340e6, 7_619e6),
        ),
        _dcf([.05,.05,.04,.04,.03], [.37,.38,.38,.39,.39], .35, .04, .182,
             .043, .055, 0.95, .05, .21, .40, .02, 2_135e6, 37_643e6),
    ),
}


# ── Industry Benchmark Data ──────────────────────────────────────────────────
# Median values by industry for benchmarking radar charts and percentile rankings
INDUSTRY_BENCHMARKS = {
    "Technology / SaaS": {
        "current_ratio": {"p25": 1.5, "median": 2.2, "p75": 3.5},
        "quick_ratio": {"p25": 1.2, "median": 1.9, "p75": 3.0},
        "gross_margin": {"p25": 0.55, "median": 0.68, "p75": 0.78},
        "operating_margin": {"p25": 0.02, "median": 0.12, "p75": 0.22},
        "net_margin": {"p25": -0.02, "median": 0.08, "p75": 0.18},
        "roa": {"p25": 0.01, "median": 0.06, "p75": 0.12},
        "roe": {"p25": 0.03, "median": 0.12, "p75": 0.22},
        "debt_to_equity": {"p25": 0.15, "median": 0.45, "p75": 0.90},
        "interest_coverage": {"p25": 3.0, "median": 8.0, "p75": 20.0},
        "asset_turnover": {"p25": 0.4, "median": 0.65, "p75": 0.90},
        "dso": {"p25": 45, "median": 65, "p75": 85},
        "cash_conversion_cycle": {"p25": 30, "median": 55, "p75": 80},
    },
    "Manufacturing": {
        "current_ratio": {"p25": 1.3, "median": 1.8, "p75": 2.5},
        "quick_ratio": {"p25": 0.7, "median": 1.1, "p75": 1.6},
        "gross_margin": {"p25": 0.22, "median": 0.30, "p75": 0.40},
        "operating_margin": {"p25": 0.03, "median": 0.08, "p75": 0.13},
        "net_margin": {"p25": 0.01, "median": 0.05, "p75": 0.09},
        "roa": {"p25": 0.02, "median": 0.05, "p75": 0.09},
        "roe": {"p25": 0.05, "median": 0.12, "p75": 0.18},
        "debt_to_equity": {"p25": 0.30, "median": 0.70, "p75": 1.30},
        "interest_coverage": {"p25": 2.5, "median": 5.0, "p75": 10.0},
        "asset_turnover": {"p25": 0.7, "median": 1.0, "p75": 1.4},
        "dso": {"p25": 35, "median": 50, "p75": 70},
        "cash_conversion_cycle": {"p25": 40, "median": 65, "p75": 90},
    },
    "Retail": {
        "current_ratio": {"p25": 0.9, "median": 1.3, "p75": 1.8},
        "quick_ratio": {"p25": 0.3, "median": 0.5, "p75": 0.9},
        "gross_margin": {"p25": 0.25, "median": 0.33, "p75": 0.42},
        "operating_margin": {"p25": 0.01, "median": 0.05, "p75": 0.09},
        "net_margin": {"p25": 0.00, "median": 0.03, "p75": 0.06},
        "roa": {"p25": 0.02, "median": 0.05, "p75": 0.09},
        "roe": {"p25": 0.05, "median": 0.14, "p75": 0.22},
        "debt_to_equity": {"p25": 0.40, "median": 1.00, "p75": 2.00},
        "interest_coverage": {"p25": 2.0, "median": 5.0, "p75": 10.0},
        "asset_turnover": {"p25": 1.2, "median": 1.8, "p75": 2.5},
        "dso": {"p25": 3, "median": 8, "p75": 20},
        "cash_conversion_cycle": {"p25": 20, "median": 40, "p75": 65},
    },
    "Healthcare": {
        "current_ratio": {"p25": 1.2, "median": 1.8, "p75": 2.8},
        "quick_ratio": {"p25": 0.8, "median": 1.4, "p75": 2.2},
        "gross_margin": {"p25": 0.35, "median": 0.50, "p75": 0.65},
        "operating_margin": {"p25": 0.00, "median": 0.08, "p75": 0.16},
        "net_margin": {"p25": -0.02, "median": 0.05, "p75": 0.12},
        "roa": {"p25": 0.01, "median": 0.05, "p75": 0.10},
        "roe": {"p25": 0.03, "median": 0.10, "p75": 0.18},
        "debt_to_equity": {"p25": 0.20, "median": 0.60, "p75": 1.20},
        "interest_coverage": {"p25": 2.5, "median": 6.0, "p75": 15.0},
        "asset_turnover": {"p25": 0.4, "median": 0.65, "p75": 0.90},
        "dso": {"p25": 40, "median": 60, "p75": 85},
        "cash_conversion_cycle": {"p25": 30, "median": 55, "p75": 80},
    },
    "Financial Services": {
        "current_ratio": {"p25": 1.0, "median": 1.3, "p75": 1.8},
        "quick_ratio": {"p25": 0.8, "median": 1.1, "p75": 1.6},
        "gross_margin": {"p25": 0.45, "median": 0.60, "p75": 0.75},
        "operating_margin": {"p25": 0.10, "median": 0.22, "p75": 0.35},
        "net_margin": {"p25": 0.05, "median": 0.15, "p75": 0.25},
        "roa": {"p25": 0.003, "median": 0.01, "p75": 0.02},
        "roe": {"p25": 0.06, "median": 0.10, "p75": 0.15},
        "debt_to_equity": {"p25": 1.50, "median": 4.00, "p75": 8.00},
        "interest_coverage": {"p25": 1.5, "median": 3.0, "p75": 6.0},
        "asset_turnover": {"p25": 0.03, "median": 0.06, "p75": 0.10},
        "dso": {"p25": 30, "median": 60, "p75": 90},
        "cash_conversion_cycle": {"p25": None, "median": None, "p75": None},
    },
    "Energy": {
        "current_ratio": {"p25": 0.9, "median": 1.3, "p75": 1.8},
        "quick_ratio": {"p25": 0.5, "median": 0.9, "p75": 1.4},
        "gross_margin": {"p25": 0.20, "median": 0.35, "p75": 0.50},
        "operating_margin": {"p25": 0.02, "median": 0.10, "p75": 0.20},
        "net_margin": {"p25": -0.02, "median": 0.06, "p75": 0.14},
        "roa": {"p25": 0.01, "median": 0.04, "p75": 0.08},
        "roe": {"p25": 0.03, "median": 0.10, "p75": 0.18},
        "debt_to_equity": {"p25": 0.40, "median": 0.80, "p75": 1.60},
        "interest_coverage": {"p25": 2.0, "median": 5.0, "p75": 12.0},
        "asset_turnover": {"p25": 0.3, "median": 0.55, "p75": 0.80},
        "dso": {"p25": 30, "median": 50, "p75": 70},
        "cash_conversion_cycle": {"p25": 20, "median": 45, "p75": 75},
    },
    "Real Estate": {
        "current_ratio": {"p25": 0.6, "median": 1.0, "p75": 1.5},
        "quick_ratio": {"p25": 0.4, "median": 0.8, "p75": 1.2},
        "gross_margin": {"p25": 0.30, "median": 0.50, "p75": 0.65},
        "operating_margin": {"p25": 0.10, "median": 0.25, "p75": 0.40},
        "net_margin": {"p25": 0.05, "median": 0.15, "p75": 0.30},
        "roa": {"p25": 0.01, "median": 0.03, "p75": 0.05},
        "roe": {"p25": 0.03, "median": 0.07, "p75": 0.12},
        "debt_to_equity": {"p25": 0.80, "median": 1.50, "p75": 3.00},
        "interest_coverage": {"p25": 1.5, "median": 2.5, "p75": 5.0},
        "asset_turnover": {"p25": 0.05, "median": 0.10, "p75": 0.18},
        "dso": {"p25": 20, "median": 40, "p75": 70},
        "cash_conversion_cycle": {"p25": None, "median": None, "p75": None},
    },
    "Consumer Goods": {
        "current_ratio": {"p25": 1.1, "median": 1.6, "p75": 2.3},
        "quick_ratio": {"p25": 0.5, "median": 0.9, "p75": 1.4},
        "gross_margin": {"p25": 0.30, "median": 0.40, "p75": 0.52},
        "operating_margin": {"p25": 0.04, "median": 0.10, "p75": 0.16},
        "net_margin": {"p25": 0.02, "median": 0.06, "p75": 0.11},
        "roa": {"p25": 0.03, "median": 0.07, "p75": 0.12},
        "roe": {"p25": 0.08, "median": 0.16, "p75": 0.25},
        "debt_to_equity": {"p25": 0.30, "median": 0.70, "p75": 1.30},
        "interest_coverage": {"p25": 3.0, "median": 7.0, "p75": 15.0},
        "asset_turnover": {"p25": 0.7, "median": 1.0, "p75": 1.4},
        "dso": {"p25": 25, "median": 40, "p75": 60},
        "cash_conversion_cycle": {"p25": 30, "median": 55, "p75": 80},
    },
    "Telecommunications": {
        "current_ratio": {"p25": 0.7, "median": 1.0, "p75": 1.5},
        "quick_ratio": {"p25": 0.5, "median": 0.8, "p75": 1.2},
        "gross_margin": {"p25": 0.35, "median": 0.50, "p75": 0.60},
        "operating_margin": {"p25": 0.05, "median": 0.15, "p75": 0.25},
        "net_margin": {"p25": 0.02, "median": 0.08, "p75": 0.15},
        "roa": {"p25": 0.02, "median": 0.05, "p75": 0.08},
        "roe": {"p25": 0.05, "median": 0.12, "p75": 0.20},
        "debt_to_equity": {"p25": 0.60, "median": 1.20, "p75": 2.50},
        "interest_coverage": {"p25": 2.0, "median": 4.0, "p75": 8.0},
        "asset_turnover": {"p25": 0.3, "median": 0.5, "p75": 0.7},
        "dso": {"p25": 30, "median": 45, "p75": 65},
        "cash_conversion_cycle": {"p25": 10, "median": 30, "p75": 55},
    },
    "Utilities": {
        "current_ratio": {"p25": 0.6, "median": 0.9, "p75": 1.3},
        "quick_ratio": {"p25": 0.4, "median": 0.7, "p75": 1.0},
        "gross_margin": {"p25": 0.25, "median": 0.40, "p75": 0.55},
        "operating_margin": {"p25": 0.10, "median": 0.18, "p75": 0.28},
        "net_margin": {"p25": 0.05, "median": 0.10, "p75": 0.18},
        "roa": {"p25": 0.01, "median": 0.03, "p75": 0.05},
        "roe": {"p25": 0.04, "median": 0.08, "p75": 0.12},
        "debt_to_equity": {"p25": 0.80, "median": 1.40, "p75": 2.20},
        "interest_coverage": {"p25": 2.0, "median": 3.5, "p75": 6.0},
        "asset_turnover": {"p25": 0.2, "median": 0.3, "p75": 0.45},
        "dso": {"p25": 25, "median": 38, "p75": 55},
        "cash_conversion_cycle": {"p25": 5, "median": 20, "p75": 40},
    },
}


# ── Company Size Definitions ─────────────────────────────────────────────────
COMPANY_SIZES = [
    "Micro-Cap (under $300M revenue)",
    "Small-Cap ($300M - $2B revenue)",
    "Mid-Cap ($2B - $10B revenue)",
    "Large-Cap ($10B - $50B revenue)",
    "Mega-Cap (over $50B revenue)",
]

# Revenue thresholds for auto-detection (upper bound for each tier)
_SIZE_THRESHOLDS = [
    (300_000_000, COMPANY_SIZES[0]),
    (2_000_000_000, COMPANY_SIZES[1]),
    (10_000_000_000, COMPANY_SIZES[2]),
    (50_000_000_000, COMPANY_SIZES[3]),
]


def detect_company_size(revenue: float) -> str:
    """Return the company size label based on revenue."""
    if revenue is None or revenue <= 0:
        return COMPANY_SIZES[1]  # default Small-Cap
    for threshold, label in _SIZE_THRESHOLDS:
        if revenue < threshold:
            return label
    return COMPANY_SIZES[4]  # Mega-Cap


# ── Size Adjustment Multipliers ──────────────────────────────────────────────
# Smaller companies typically have:
#   • Higher liquidity ratios (more cash-heavy balance sheets)
#   • Lower margins (less scale advantage)
#   • Higher leverage variance
#   • Lower asset turnover
# These multipliers are applied to the base industry benchmarks (p25/median/p75)
# to produce size-adjusted peer comparisons.
#
# Format: { ratio_key: (p25_mult, median_mult, p75_mult) }
# A multiplier > 1 raises the benchmark, < 1 lowers it.

_SIZE_ADJUSTMENTS = {
    COMPANY_SIZES[0]: {  # Micro-Cap
        "current_ratio":     (1.15, 1.10, 1.20),
        "quick_ratio":       (1.15, 1.10, 1.20),
        "gross_margin":      (0.85, 0.88, 0.90),
        "operating_margin":  (0.70, 0.75, 0.80),
        "net_margin":        (0.65, 0.70, 0.75),
        "roa":               (0.80, 0.85, 0.90),
        "roe":               (0.85, 0.90, 0.95),
        "debt_to_equity":    (1.10, 1.15, 1.25),
        "interest_coverage": (0.70, 0.75, 0.80),
        "asset_turnover":    (0.90, 0.92, 0.95),
        "dso":               (1.10, 1.15, 1.20),
        "cash_conversion_cycle": (1.10, 1.15, 1.25),
    },
    COMPANY_SIZES[1]: {  # Small-Cap
        "current_ratio":     (1.05, 1.05, 1.08),
        "quick_ratio":       (1.05, 1.05, 1.08),
        "gross_margin":      (0.92, 0.94, 0.95),
        "operating_margin":  (0.85, 0.88, 0.90),
        "net_margin":        (0.82, 0.85, 0.88),
        "roa":               (0.90, 0.92, 0.95),
        "roe":               (0.92, 0.95, 0.97),
        "debt_to_equity":    (1.05, 1.08, 1.12),
        "interest_coverage": (0.85, 0.88, 0.90),
        "asset_turnover":    (0.95, 0.96, 0.98),
        "dso":               (1.05, 1.08, 1.10),
        "cash_conversion_cycle": (1.05, 1.08, 1.12),
    },
    COMPANY_SIZES[2]: {  # Mid-Cap — baseline, no adjustment
    },
    COMPANY_SIZES[3]: {  # Large-Cap
        "current_ratio":     (0.95, 0.97, 0.95),
        "quick_ratio":       (0.95, 0.97, 0.95),
        "gross_margin":      (1.05, 1.04, 1.03),
        "operating_margin":  (1.10, 1.08, 1.06),
        "net_margin":        (1.10, 1.08, 1.06),
        "roa":               (1.05, 1.04, 1.03),
        "roe":               (1.05, 1.04, 1.03),
        "debt_to_equity":    (0.95, 0.93, 0.90),
        "interest_coverage": (1.10, 1.12, 1.15),
        "asset_turnover":    (1.03, 1.04, 1.05),
        "dso":               (0.95, 0.93, 0.90),
        "cash_conversion_cycle": (0.95, 0.93, 0.90),
    },
    COMPANY_SIZES[4]: {  # Mega-Cap
        "current_ratio":     (0.90, 0.92, 0.90),
        "quick_ratio":       (0.90, 0.92, 0.90),
        "gross_margin":      (1.08, 1.07, 1.05),
        "operating_margin":  (1.18, 1.15, 1.10),
        "net_margin":        (1.18, 1.15, 1.10),
        "roa":               (1.08, 1.06, 1.05),
        "roe":               (1.08, 1.06, 1.05),
        "debt_to_equity":    (0.88, 0.85, 0.82),
        "interest_coverage": (1.20, 1.25, 1.30),
        "asset_turnover":    (1.05, 1.06, 1.08),
        "dso":               (0.90, 0.88, 0.85),
        "cash_conversion_cycle": (0.88, 0.85, 0.82),
    },
}


def get_size_adjusted_benchmarks(industry: str, company_size: str) -> dict:
    """
    Return industry benchmarks adjusted for company size.
    Mid-Cap returns the base benchmarks unchanged.
    """
    base = INDUSTRY_BENCHMARKS.get(industry, {})
    adjustments = _SIZE_ADJUSTMENTS.get(company_size, {})
    if not adjustments:
        return base  # Mid-Cap or unknown size — use base

    adjusted = {}
    for ratio_key, bm in base.items():
        mults = adjustments.get(ratio_key)
        if mults and bm.get("median") is not None:
            p25_m, med_m, p75_m = mults
            adjusted[ratio_key] = {
                "p25": round(bm["p25"] * p25_m, 4) if bm.get("p25") is not None else None,
                "median": round(bm["median"] * med_m, 4),
                "p75": round(bm["p75"] * p75_m, 4) if bm.get("p75") is not None else None,
            }
        else:
            adjusted[ratio_key] = bm
    return adjusted


_LOWER_IS_BETTER_RATIOS = {
    "debt_to_equity", "debt_to_assets", "lt_debt_ratio",
    "dso", "cash_conversion_cycle", "accruals_ratio", "equity_multiplier",
}


def get_percentile(value, benchmarks: dict, ratio_key: str = "") -> str:
    """Determine approximate percentile ranking against industry benchmarks.

    For lower-is-better ratios (debt, DSO, etc.), the scale is inverted
    so that a low value correctly maps to Top Quartile.
    """
    if value is None or not benchmarks or benchmarks.get("median") is None:
        return "N/A"
    p25 = benchmarks.get("p25", 0)
    median = benchmarks.get("median", 0)
    p75 = benchmarks.get("p75", 0)

    if ratio_key in _LOWER_IS_BETTER_RATIOS:
        # Lower is better: below p25 = top quartile
        if value <= p25:
            return "Top Quartile (>75th)"
        elif value <= median:
            return "Above Median (50-75th)"
        elif value <= p75:
            return "Below Median (25-50th)"
        else:
            return "Bottom Quartile (<25th)"
    else:
        if value >= p75:
            return "Top Quartile (>75th)"
        elif value >= median:
            return "Above Median (50-75th)"
        elif value >= p25:
            return "Below Median (25-50th)"
        else:
            return "Bottom Quartile (<25th)"
