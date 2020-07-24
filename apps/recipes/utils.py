from apps.food.utils import get_serving_size


class DailyBoxResponse(object):
    count = 0

    def bfs(self, candidates, target, result, valuelist, start):
        if self.count == 1:
            return result
        if target['fat_total'] > target['daily_fat_intake_min'] and target['fiber_total'] > target[
            'daily_fiber_intake_min'] and target['carb_total'] > target['daily_carbohydrates_intake_min'] and target[
            'protein_total'] > target['daily_protein_intake_min'] and valuelist not in result:
            self.count = self.count + 1
            return result.append(valuelist)

        for index in range(start, len(candidates)):
            if getattr(candidates[index], 'ingredient', None):
                user_ingredient = candidates[index].ingredient
            else:
                user_ingredient = candidates[index]

            protein = 0 if user_ingredient.protein is None else user_ingredient.protein
            carbohydrate = 0 if user_ingredient.carbohydrate is None else user_ingredient.carbohydrate
            fat = 0 if user_ingredient.fat is None else user_ingredient.fat
            fiber = 0 if user_ingredient.fiber is None else user_ingredient.fiber

            serving_size = get_serving_size(user_ingredient)

            protein = (float(protein) * serving_size) / 100
            carbohydrate = (float(carbohydrate) * serving_size) / 100
            fat = (float(fat) * serving_size) / 100
            fiber = (float(fiber) * serving_size) / 100

            if target['daily_fat_intake_max'] < fat or target['daily_carbohydrates_intake_max'] < carbohydrate or \
                    target['daily_protein_intake_max'] < protein or target['daily_fiber_intake_max'] < fiber:
                return
            self.bfs(candidates, {
                'daily_fat_intake_max': target['daily_fat_intake_max'] - fat,
                'daily_carbohydrates_intake_max': target['daily_carbohydrates_intake_max'] - carbohydrate,
                'daily_protein_intake_max': target['daily_protein_intake_max'] - protein,
                'daily_fiber_intake_max': target['daily_fiber_intake_max'] - fiber,

                'daily_fat_intake_min': target['daily_fat_intake_min'],
                'daily_carbohydrates_intake_min': target['daily_carbohydrates_intake_min'],
                'daily_protein_intake_min': target['daily_protein_intake_min'],
                'daily_fiber_intake_min': target['daily_fiber_intake_min'],

                'fat_total': target['fat_total'] + fat,
                'fiber_total': target['fiber_total'] + fiber,
                'carb_total': target['carb_total'] + carbohydrate,
                'protein_total': target['protein_total'] + protein,
            }, result, valuelist + [user_ingredient.pk], index + 1)

    def combinationSum2(self, candidates, target):

        result = []
        self.bfs(candidates, target, result, [], 0)
        return result
