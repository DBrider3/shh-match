import { z } from 'zod';

export const ProfileSchema = z.object({
  nickname: z.string().min(2, '닉네임은 최소 2자 이상이어야 합니다.').max(20, '닉네임은 20자를 초과할 수 없습니다.'),
  gender: z.enum(['M','F'], { message: '성별을 선택해주세요.' }),
  birthYear: z.number()
    .min(1950, '출생연도가 너무 이릅니다.')
    .max(new Date().getFullYear()-19, '만 19세 이상만 가입 가능합니다.'),
  height: z.number().int().min(120).max(220).optional(),
  region: z.string().max(30).optional(),
  job: z.string().max(30).optional(),
  intro: z.string().max(500, '자기소개는 500자를 초과할 수 없습니다.').optional(),
  photos: z.array(z.string().url('올바른 URL 형식이어야 합니다.')).max(6, '사진은 최대 6장까지 업로드 가능합니다.'),
  visible: z.object({
    age: z.boolean(),
    height: z.boolean(),
    region: z.boolean(),
    job: z.boolean(),
    intro: z.boolean(),
  })
});

export const PreferencesSchema = z.object({
  targetGender: z.enum(['M','F'], { message: '선호 성별을 선택해주세요.' }),
  ageMin: z.number().min(19, '최소 연령은 19세 이상이어야 합니다.').max(100),
  ageMax: z.number().min(19).max(100, '최대 연령은 100세를 초과할 수 없습니다.'),
  regions: z.array(z.string()).max(10, '지역은 최대 10개까지 선택 가능합니다.'),
  keywords: z.array(z.string()).max(20, '키워드는 최대 20개까지 선택 가능합니다.'),
  blocks: z.array(z.string())
}).refine(data => data.ageMin <= data.ageMax, {
  message: '최소 연령은 최대 연령보다 작아야 합니다.',
  path: ['ageMax']
});

export const LikeSchema = z.object({
  toUserId: z.string().min(1, '사용자 ID가 필요합니다.'),
  batchWeek: z.string().regex(/^\d{4}-W\d{2}$/, '올바른 주차 형식이 아닙니다.')
});

export const PaymentIntentSchema = z.object({
  matchId: z.string().min(1, '매칭 ID가 필요합니다.')
});

export type ProfileFormData = z.infer<typeof ProfileSchema>;
export type PreferencesFormData = z.infer<typeof PreferencesSchema>;
export type LikeFormData = z.infer<typeof LikeSchema>;
export type PaymentIntentFormData = z.infer<typeof PaymentIntentSchema>;