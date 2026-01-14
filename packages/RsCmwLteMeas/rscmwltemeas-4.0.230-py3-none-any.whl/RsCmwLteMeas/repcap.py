from enum import Enum
# noinspection PyPep8Naming
from .Internal.RepeatedCapability import VALUE_DEFAULT as DefaultRepCap
# noinspection PyPep8Naming
from .Internal.RepeatedCapability import VALUE_EMPTY as EmptyRepCap
# noinspection PyPep8Naming,PyUnresolvedReferences
from .Internal.RepeatedCapability import VALUE_SKIP_HEADER as SkipHeaderRepCap


# noinspection SpellCheckingInspection
class Instance(Enum):
	"""Global Repeated capability Instance"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Inst1 = 1
	Inst2 = 2
	Inst3 = 3
	Inst4 = 4
	Inst5 = 5
	Inst6 = 6
	Inst7 = 7
	Inst8 = 8
	Inst9 = 9
	Inst10 = 10
	Inst11 = 11
	Inst12 = 12
	Inst13 = 13
	Inst14 = 14
	Inst15 = 15
	Inst16 = 16


# noinspection SpellCheckingInspection
class AbsMarker(Enum):
	"""Repeated capability AbsMarker"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Area(Enum):
	"""Repeated capability Area"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12


# noinspection SpellCheckingInspection
class CarrierComponent(Enum):
	"""Repeated capability CarrierComponent"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	SkipCc = SkipHeaderRepCap
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4


# noinspection SpellCheckingInspection
class ChannelBw(Enum):
	"""Repeated capability ChannelBw"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Bw14 = 14
	Bw30 = 30
	Bw50 = 50
	Bw100 = 100
	Bw150 = 150
	Bw200 = 200


# noinspection SpellCheckingInspection
class DeltaMarker(Enum):
	"""Repeated capability DeltaMarker"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Difference(Enum):
	"""Repeated capability Difference"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class EutraBand(Enum):
	"""Repeated capability EutraBand"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr30 = 30
	Nr50 = 50


# noinspection SpellCheckingInspection
class FirstChannelBw(Enum):
	"""Repeated capability FirstChannelBw"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Bw100 = 100
	Bw150 = 150
	Bw200 = 200


# noinspection SpellCheckingInspection
class Limit(Enum):
	"""Repeated capability Limit"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12


# noinspection SpellCheckingInspection
class MaxRange(Enum):
	"""Repeated capability MaxRange"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class MinRange(Enum):
	"""Repeated capability MinRange"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class Preamble(Enum):
	"""Repeated capability Preamble"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32
	Nr33 = 33
	Nr34 = 34
	Nr35 = 35
	Nr36 = 36
	Nr37 = 37
	Nr38 = 38
	Nr39 = 39
	Nr40 = 40
	Nr41 = 41
	Nr42 = 42
	Nr43 = 43
	Nr44 = 44
	Nr45 = 45
	Nr46 = 46
	Nr47 = 47
	Nr48 = 48
	Nr49 = 49
	Nr50 = 50
	Nr51 = 51
	Nr52 = 52
	Nr53 = 53
	Nr54 = 54
	Nr55 = 55
	Nr56 = 56
	Nr57 = 57
	Nr58 = 58
	Nr59 = 59
	Nr60 = 60
	Nr61 = 61
	Nr62 = 62
	Nr63 = 63
	Nr64 = 64
	Nr65 = 65
	Nr66 = 66
	Nr67 = 67
	Nr68 = 68
	Nr69 = 69
	Nr70 = 70
	Nr71 = 71
	Nr72 = 72
	Nr73 = 73
	Nr74 = 74
	Nr75 = 75
	Nr76 = 76
	Nr77 = 77
	Nr78 = 78
	Nr79 = 79
	Nr80 = 80
	Nr81 = 81
	Nr82 = 82
	Nr83 = 83
	Nr84 = 84
	Nr85 = 85
	Nr86 = 86
	Nr87 = 87
	Nr88 = 88
	Nr89 = 89
	Nr90 = 90
	Nr91 = 91
	Nr92 = 92
	Nr93 = 93
	Nr94 = 94
	Nr95 = 95
	Nr96 = 96
	Nr97 = 97
	Nr98 = 98
	Nr99 = 99
	Nr100 = 100
	Nr101 = 101
	Nr102 = 102
	Nr103 = 103
	Nr104 = 104
	Nr105 = 105
	Nr106 = 106
	Nr107 = 107
	Nr108 = 108
	Nr109 = 109
	Nr110 = 110
	Nr111 = 111
	Nr112 = 112
	Nr113 = 113
	Nr114 = 114
	Nr115 = 115
	Nr116 = 116
	Nr117 = 117
	Nr118 = 118
	Nr119 = 119
	Nr120 = 120
	Nr121 = 121
	Nr122 = 122
	Nr123 = 123
	Nr124 = 124
	Nr125 = 125
	Nr126 = 126
	Nr127 = 127
	Nr128 = 128
	Nr129 = 129
	Nr130 = 130
	Nr131 = 131
	Nr132 = 132
	Nr133 = 133
	Nr134 = 134
	Nr135 = 135
	Nr136 = 136
	Nr137 = 137
	Nr138 = 138
	Nr139 = 139
	Nr140 = 140
	Nr141 = 141
	Nr142 = 142
	Nr143 = 143
	Nr144 = 144
	Nr145 = 145
	Nr146 = 146
	Nr147 = 147
	Nr148 = 148
	Nr149 = 149
	Nr150 = 150
	Nr151 = 151
	Nr152 = 152
	Nr153 = 153
	Nr154 = 154
	Nr155 = 155
	Nr156 = 156
	Nr157 = 157
	Nr158 = 158
	Nr159 = 159
	Nr160 = 160
	Nr161 = 161
	Nr162 = 162
	Nr163 = 163
	Nr164 = 164
	Nr165 = 165
	Nr166 = 166
	Nr167 = 167
	Nr168 = 168
	Nr169 = 169
	Nr170 = 170
	Nr171 = 171
	Nr172 = 172
	Nr173 = 173
	Nr174 = 174
	Nr175 = 175
	Nr176 = 176
	Nr177 = 177
	Nr178 = 178
	Nr179 = 179
	Nr180 = 180
	Nr181 = 181
	Nr182 = 182
	Nr183 = 183
	Nr184 = 184
	Nr185 = 185
	Nr186 = 186
	Nr187 = 187
	Nr188 = 188
	Nr189 = 189
	Nr190 = 190
	Nr191 = 191
	Nr192 = 192
	Nr193 = 193
	Nr194 = 194
	Nr195 = 195
	Nr196 = 196
	Nr197 = 197
	Nr198 = 198
	Nr199 = 199
	Nr200 = 200
	Nr201 = 201
	Nr202 = 202
	Nr203 = 203
	Nr204 = 204
	Nr205 = 205
	Nr206 = 206
	Nr207 = 207
	Nr208 = 208
	Nr209 = 209
	Nr210 = 210
	Nr211 = 211
	Nr212 = 212
	Nr213 = 213
	Nr214 = 214
	Nr215 = 215
	Nr216 = 216
	Nr217 = 217
	Nr218 = 218
	Nr219 = 219
	Nr220 = 220
	Nr221 = 221
	Nr222 = 222
	Nr223 = 223
	Nr224 = 224
	Nr225 = 225
	Nr226 = 226
	Nr227 = 227
	Nr228 = 228
	Nr229 = 229
	Nr230 = 230
	Nr231 = 231
	Nr232 = 232
	Nr233 = 233
	Nr234 = 234
	Nr235 = 235
	Nr236 = 236
	Nr237 = 237
	Nr238 = 238
	Nr239 = 239
	Nr240 = 240
	Nr241 = 241
	Nr242 = 242
	Nr243 = 243
	Nr244 = 244
	Nr245 = 245
	Nr246 = 246
	Nr247 = 247
	Nr248 = 248
	Nr249 = 249
	Nr250 = 250
	Nr251 = 251
	Nr252 = 252
	Nr253 = 253
	Nr254 = 254
	Nr255 = 255
	Nr256 = 256
	Nr257 = 257
	Nr258 = 258
	Nr259 = 259
	Nr260 = 260
	Nr261 = 261
	Nr262 = 262
	Nr263 = 263
	Nr264 = 264
	Nr265 = 265
	Nr266 = 266
	Nr267 = 267
	Nr268 = 268
	Nr269 = 269
	Nr270 = 270
	Nr271 = 271
	Nr272 = 272
	Nr273 = 273
	Nr274 = 274
	Nr275 = 275
	Nr276 = 276
	Nr277 = 277
	Nr278 = 278
	Nr279 = 279
	Nr280 = 280
	Nr281 = 281
	Nr282 = 282
	Nr283 = 283
	Nr284 = 284
	Nr285 = 285
	Nr286 = 286
	Nr287 = 287
	Nr288 = 288
	Nr289 = 289
	Nr290 = 290
	Nr291 = 291
	Nr292 = 292
	Nr293 = 293
	Nr294 = 294
	Nr295 = 295
	Nr296 = 296
	Nr297 = 297
	Nr298 = 298
	Nr299 = 299
	Nr300 = 300
	Nr301 = 301
	Nr302 = 302
	Nr303 = 303
	Nr304 = 304
	Nr305 = 305
	Nr306 = 306
	Nr307 = 307
	Nr308 = 308
	Nr309 = 309
	Nr310 = 310
	Nr311 = 311
	Nr312 = 312
	Nr313 = 313
	Nr314 = 314
	Nr315 = 315
	Nr316 = 316
	Nr317 = 317
	Nr318 = 318
	Nr319 = 319
	Nr320 = 320
	Nr321 = 321
	Nr322 = 322
	Nr323 = 323
	Nr324 = 324
	Nr325 = 325
	Nr326 = 326
	Nr327 = 327
	Nr328 = 328
	Nr329 = 329
	Nr330 = 330
	Nr331 = 331
	Nr332 = 332
	Nr333 = 333
	Nr334 = 334
	Nr335 = 335
	Nr336 = 336
	Nr337 = 337
	Nr338 = 338
	Nr339 = 339
	Nr340 = 340
	Nr341 = 341
	Nr342 = 342
	Nr343 = 343
	Nr344 = 344
	Nr345 = 345
	Nr346 = 346
	Nr347 = 347
	Nr348 = 348
	Nr349 = 349
	Nr350 = 350
	Nr351 = 351
	Nr352 = 352
	Nr353 = 353
	Nr354 = 354
	Nr355 = 355
	Nr356 = 356
	Nr357 = 357
	Nr358 = 358
	Nr359 = 359
	Nr360 = 360
	Nr361 = 361
	Nr362 = 362
	Nr363 = 363
	Nr364 = 364
	Nr365 = 365
	Nr366 = 366
	Nr367 = 367
	Nr368 = 368
	Nr369 = 369
	Nr370 = 370
	Nr371 = 371
	Nr372 = 372
	Nr373 = 373
	Nr374 = 374
	Nr375 = 375
	Nr376 = 376
	Nr377 = 377
	Nr378 = 378
	Nr379 = 379
	Nr380 = 380
	Nr381 = 381
	Nr382 = 382
	Nr383 = 383
	Nr384 = 384
	Nr385 = 385
	Nr386 = 386
	Nr387 = 387
	Nr388 = 388
	Nr389 = 389
	Nr390 = 390
	Nr391 = 391
	Nr392 = 392
	Nr393 = 393
	Nr394 = 394
	Nr395 = 395
	Nr396 = 396
	Nr397 = 397
	Nr398 = 398
	Nr399 = 399
	Nr400 = 400


# noinspection SpellCheckingInspection
class PreambleFormat(Enum):
	"""Repeated capability PreambleFormat"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Fmt1 = 1
	Fmt2 = 2
	Fmt3 = 3
	Fmt4 = 4
	Fmt5 = 5


# noinspection SpellCheckingInspection
class QAMmodOrder(Enum):
	"""Repeated capability QAMmodOrder"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Qam16 = 16
	Qam64 = 64
	Qam256 = 256


# noinspection SpellCheckingInspection
class RBcount(Enum):
	"""Repeated capability RBcount"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class RBoffset(Enum):
	"""Repeated capability RBoffset"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class RBWkHz(Enum):
	"""Repeated capability RBWkHz"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Rbw30 = 30
	Rbw50 = 50
	Rbw100 = 100
	Rbw150 = 150
	Rbw200 = 200
	Rbw1000 = 1000


# noinspection SpellCheckingInspection
class Ripple(Enum):
	"""Repeated capability Ripple"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2


# noinspection SpellCheckingInspection
class SecondaryCC(Enum):
	"""Repeated capability SecondaryCC"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	SkipCc = SkipHeaderRepCap
	CC1 = 1
	CC2 = 2
	CC3 = 3
	CC4 = 4
	CC5 = 5
	CC6 = 6
	CC7 = 7


# noinspection SpellCheckingInspection
class SecondChannelBw(Enum):
	"""Repeated capability SecondChannelBw"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Bw50 = 50
	Bw100 = 100
	Bw150 = 150
	Bw200 = 200


# noinspection SpellCheckingInspection
class Segment(Enum):
	"""Repeated capability Segment"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5
	Nr6 = 6
	Nr7 = 7
	Nr8 = 8
	Nr9 = 9
	Nr10 = 10
	Nr11 = 11
	Nr12 = 12
	Nr13 = 13
	Nr14 = 14
	Nr15 = 15
	Nr16 = 16
	Nr17 = 17
	Nr18 = 18
	Nr19 = 19
	Nr20 = 20
	Nr21 = 21
	Nr22 = 22
	Nr23 = 23
	Nr24 = 24
	Nr25 = 25
	Nr26 = 26
	Nr27 = 27
	Nr28 = 28
	Nr29 = 29
	Nr30 = 30
	Nr31 = 31
	Nr32 = 32
	Nr33 = 33
	Nr34 = 34
	Nr35 = 35
	Nr36 = 36
	Nr37 = 37
	Nr38 = 38
	Nr39 = 39
	Nr40 = 40
	Nr41 = 41
	Nr42 = 42
	Nr43 = 43
	Nr44 = 44
	Nr45 = 45
	Nr46 = 46
	Nr47 = 47
	Nr48 = 48
	Nr49 = 49
	Nr50 = 50
	Nr51 = 51
	Nr52 = 52
	Nr53 = 53
	Nr54 = 54
	Nr55 = 55
	Nr56 = 56
	Nr57 = 57
	Nr58 = 58
	Nr59 = 59
	Nr60 = 60
	Nr61 = 61
	Nr62 = 62
	Nr63 = 63
	Nr64 = 64
	Nr65 = 65
	Nr66 = 66
	Nr67 = 67
	Nr68 = 68
	Nr69 = 69
	Nr70 = 70
	Nr71 = 71
	Nr72 = 72
	Nr73 = 73
	Nr74 = 74
	Nr75 = 75
	Nr76 = 76
	Nr77 = 77
	Nr78 = 78
	Nr79 = 79
	Nr80 = 80
	Nr81 = 81
	Nr82 = 82
	Nr83 = 83
	Nr84 = 84
	Nr85 = 85
	Nr86 = 86
	Nr87 = 87
	Nr88 = 88
	Nr89 = 89
	Nr90 = 90
	Nr91 = 91
	Nr92 = 92
	Nr93 = 93
	Nr94 = 94
	Nr95 = 95
	Nr96 = 96
	Nr97 = 97
	Nr98 = 98
	Nr99 = 99
	Nr100 = 100
	Nr101 = 101
	Nr102 = 102
	Nr103 = 103
	Nr104 = 104
	Nr105 = 105
	Nr106 = 106
	Nr107 = 107
	Nr108 = 108
	Nr109 = 109
	Nr110 = 110
	Nr111 = 111
	Nr112 = 112
	Nr113 = 113
	Nr114 = 114
	Nr115 = 115
	Nr116 = 116
	Nr117 = 117
	Nr118 = 118
	Nr119 = 119
	Nr120 = 120
	Nr121 = 121
	Nr122 = 122
	Nr123 = 123
	Nr124 = 124
	Nr125 = 125
	Nr126 = 126
	Nr127 = 127
	Nr128 = 128


# noinspection SpellCheckingInspection
class Table(Enum):
	"""Repeated capability Table"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Nr1 = 1
	Nr2 = 2
	Nr3 = 3
	Nr4 = 4
	Nr5 = 5


# noinspection SpellCheckingInspection
class ThirdChannelBw(Enum):
	"""Repeated capability ThirdChannelBw"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Bw100 = 100
	Bw150 = 150
	Bw200 = 200


# noinspection SpellCheckingInspection
class UtraAdjChannel(Enum):
	"""Repeated capability UtraAdjChannel"""
	Empty = EmptyRepCap
	Default = DefaultRepCap
	
	Ch1 = 1
	Ch2 = 2
