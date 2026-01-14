from typing import Dict, List

import pandas as pd
from scipy.stats import pearsonr, spearmanr
from .md import (
    get_flac_markdown,
    get_badd_markdown,
    get_adaface_markdown,
    get_badd_json,
    get_adaface_json,
    get_flac_json,
)
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


def analysis_json(
    csv_path: str,
    task: str,
    target: str,
    sensitive: List[str],
    sp_th: float = 0.1,
    rep_th: float = 0.1,
    return_title: bool = False,
):
    df = pd.read_csv(csv_path)
    representation_bias_result = analyze_representation_bias(df, sensitive)
    representation_bias_plot = plot_representation_bias_html(df, sensitive)
    suggestions = []
    results_dict = {"task": task, "biases": [], "mitigation": []}
    bias_threshold = rep_th
    representation_biases_found = False
    for key, value in representation_bias_result.items():
        if isinstance(value, dict):
            max_proportion = max(value.values())
            min_proportion = min(value.values())
            if max_proportion - min_proportion > bias_threshold * sum(value.values()):
                suggestions.append(
                    f"There is representation bias for {key} ({(max_proportion-min_proportion)*100:.2f}% gap between most and less represented group)."
                )
                results_dict["biases"].append(suggestions[-1])
                representation_biases_found = True

    spurious_correlations = find_spurious_correlations(df, target, sensitive, sp_th)
    spurious_correlations_found = len(spurious_correlations) > 0

    if task.lower() == "face verification":
        suggestions.append(
            "Consider using AdaFace for training a fairer face verification model."
        )
        results_dict["mitigation"].append(suggestions[-1])

    elif task.lower() == "image classification":
        if len(spurious_correlations) == 1:
            suggestions.append(
                f"There is spurious correlation of {(spurious_correlations[0][2])*100:.2f}% between {spurious_correlations[0][0]} and {spurious_correlations[0][1]}."
            )
            results_dict["biases"].append(suggestions[-1])
            results_dict["mitigation"].append(
                "Consider using the FLAC method to mitigate it."
            )
        elif len(spurious_correlations) > 1:
            for tar, sen, per in spurious_correlations:
                suggestions.append(
                    f"There is spurious correlation of {per*100:.2f}% between {tar} and {sen}."
                )
                results_dict["biases"].append(suggestions[-1])
            results_dict["mitigation"].append(
                "Given that there are multiple spurious correlations, consider using the BAdd method to mitigate it."
            )

    # if len(results_dict["mitigation"]) == 0:
    #     results_dict["mitigation"].append(
    #         "Consider using the FLAC method for learning fair representations."
    #     )

    if representation_biases_found and not spurious_correlations_found:
        title = "Visual representation bias"
    elif spurious_correlations_found and not representation_biases_found:
        title = "Spurious correlations bias"
    elif spurious_correlations_found and representation_biases_found:
        title = "Spurious correlations and representation biases"
    else:
        title = "No issue detected"

    json_output = [
        {"type": "heading", "level": 1, "content": title},
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "content": "This report analyzes the dataset for representation biases and spurious correlations, providing insights and mitigation recommendations. Representation bias occurs when certain groups or attributes are underrepresented or overrepresented in a dataset, leading to learned models that perform disproportionately well or poorly across different subpopulations. Spurious correlations refer to misleading statistical dependencies between the target variable and non-causal, often bias-related, features. These correlations can cause a model to rely on superficial cues rather than meaningful, task-relevant features.",
                }
            ],
        },
        {"type": "heading", "level": 3, "content": "Representation Bias"},
        {"type": "html", "content": representation_bias_plot},
    ]

    if representation_biases_found:
        paragraph = "The analysis reveals significant representation biases across several sensitive attributes. "
        bias_descriptions = []
        for key, value in representation_bias_result.items():
            if isinstance(value, dict):
                max_proportion = max(value.values())
                min_proportion = min(value.values())
                if max_proportion - min_proportion > bias_threshold * sum(
                    value.values()
                ):
                    bias_descriptions.append(
                        f"{key} exhibits a {(max_proportion-min_proportion)*100:.2f}% gap between the most and least represented groups"
                    )
        if len(bias_descriptions) > 1:
            paragraph += (
                ", ".join(bias_descriptions[:-1])
                + " and "
                + bias_descriptions[-1]
                + ". "
            )
        else:
            paragraph += bias_descriptions[0] + ". "

        paragraph += "These imbalances suggest potential biases in model training, as underrepresented groups may receive inadequate attention."
        json_output.append(
            {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        )
    else:
        paragraph = f"The analysis indicates no significant representation biases across the sensitive attributes, as the maximum difference in representation across all target–sensitive attribute pairs remains below {rep_th*100:.1f}%. The distribution of data across different groups appears to be relatively balanced, suggesting a well-represented dataset."
        json_output.append(
            {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        )

    json_output.append(
        {"type": "heading", "level": 3, "content": "Spurious Correlations"}
    )

    if spurious_correlations_found:
        paragraph = "Spurious correlations were identified between the target variable and several sensitive attributes. "
        correlation_descriptions = []
        for tar, sen, per in spurious_correlations:
            correlation_descriptions.append(
                f"a correlation of {per*100:.2f}% was found between {tar} and the target"
            )
        if len(correlation_descriptions) > 1:
            correlation_descriptions[0] = correlation_descriptions[0].capitalize()
            paragraph += (
                ", ".join(correlation_descriptions[:-1])
                + " and "
                + correlation_descriptions[-1]
                + ", indicating strong, potentially misleading relationships. "
            )
        else:
            correlation_descriptions[0] = correlation_descriptions[0].capitalize()
            paragraph += (
                correlation_descriptions[0]
                + ", indicating a strong, potentially misleading relationship. "
            )
        paragraph += "These correlations suggest that the model may learn to rely on these attributes, leading to biased predictions."
        json_output.append(
            {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        )
    else:
        paragraph = f"No significant spurious correlations were found between the target variable and the sensitive attributes, as the maximum correlation across all target–sensitive attribute pairs remains below {sp_th:.2f}. This suggests that the model is unlikely to learn misleading relationships based on these attributes."
        json_output.append(
            {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        )

    json_output.append(
        {"type": "heading", "level": 2, "content": "Mitigation Recommendations"}
    )
    # json_output.append({"type": "paragraph", "content": f"**Task: {results_dict['task']}**"})

    if representation_biases_found or spurious_correlations_found:
        title = "Bias detected"
        paragraph = "Given the identified biases, the following mitigation strategies are recommended. \n"
        json_output.append(
            {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        )
        if representation_biases_found:
            paragraph = "For representation bias, consider techniques such as oversampling or undersampling to balance the dataset. "
            json_output.append(
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "For representation bias: \n"}
                    ],
                }
            )
            list_item = {
                "type": "list",
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "content": "- Consider techniques such as oversampling or undersampling to balance the dataset w.r.t the desired attribute. For instance, the ",
                            },
                            {
                                "type": "link",
                                "url": "https://docs.pytorch.org/docs/stable/data.html#torch.utils.data.WeightedRandomSampler",
                                "content": "WeightedRandomSampler",
                            },
                            {
                                "type": "text",
                                "content": " provided by pytorch can be used for this purpose.\n",
                            },
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "content": "- Use synthetic data generation to enhance representation balance. For instance, the ",
                            },
                            {
                                "type": "link",
                                "url": "https://github.com/gebaltso/SDFD/",
                                "content": "SDFD",
                            },
                            {
                                "type": "text",
                                "content": " is an approach that takes advantage of state-of-the-art generative models to build versatile synthetic face image data with diverse attributes. \n \n <sub>Baltsou, G., Sarridis, I., Koutlis, C., & Papadopoulos, S. (2024, May). Sdfd: Building a versatile synthetic face image dataset with diverse attributes. In *2024 IEEE 18th International Conference on Automatic Face and Gesture Recognition (FG)* (pp. 1-10). IEEE.</sub>\n",
                            },
                        ],
                    },
                ],
            }
            json_output.append(list_item)

            # json_output.append({"type": "paragraph", "content": [{"type": "text", "content": rep_bias_content}]})

        if spurious_correlations_found:
            json_output.append(
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "content": "\nFor spurious correlations: \n"}
                    ],
                }
            )
            if len(spurious_correlations) == 1:
                json_output.append(
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "content": "- Since only a single spurious correlation is present, ",
                            },
                            {
                                "type": "link",
                                "url": "https://github.com/gsarridis/FLAC",
                                "content": "FLAC",
                            },
                            {
                                "type": "text",
                                "content": " offers an effective way to mitigate its impact during training. Specifically, FLAC mitigates bias by minimizing the mutual information between the target labels and the correlated attribute. \n \n <sub>Sarridis, I., Koutlis, C., Papadopoulos, S., & Diou, C. (2024). Flac: Fairness-aware representation learning by suppressing attribute-class associations. *IEEE Transactions on Pattern Analysis and Machine Intelligence.*</sub>\n",
                            },
                        ],
                    }
                )
            else:
                json_output.append(
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "content": "- Considering that more than one attribute contributes to the spurious correlations, ",
                            },
                            {
                                "type": "link",
                                "url": "https://github.com/mever-team/vb-mitigator",
                                "content": "BAdd",
                            },
                            {
                                "type": "text",
                                "content": " is suggested as a mitigation methodology due to its effectiveness in multi-attribute bias scenarios. In particular, BAdd is a simple yet effective method that promotes learning fair representations by incorporating features representing these attributes into the backbone. \n \n <sub>Sarridis, I., Koutlis, C., Papadopoulos, S., & Diou, C. (2024). Badd: Bias mitigation through bias addition. *In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) Workshops, 2025.*</sub>\n",
                            },
                        ],
                    }
                )

        # json_output.append(
        #     {"type": "paragraph", "content": [{"type": "text", "content": paragraph}]}
        # )
    else:
        titel = "No issues found"
        paragraph = ""
        json_output.append(
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "content": "- Although no significant biases were detected, it is still recommended to employ an open-set bias mitigation approach, such as ",
                    },
                    {
                        "type": "link",
                        "url": "https://github.com/mever-team/vb-mitigator",
                        "content": "MAVias",
                    },
                    {
                        "type": "text",
                        "content": ", which automatically identifies potential biases in natural images using foundation models and allows for training a model that is not affected by these biases. \n \n <sub>Sarridis, I., Koutlis, C., Papadopoulos, S., & Diou, C. (2024). MAVias: Mitigate any Visual Bias. *In Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV), 2025.*</sub>\n",
                    },
                ],
            }
        )
    if task.lower() == "face verification":
        json_output.append(
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "content": "\nFor face verification tasks: \n"}
                ],
            }
        )

        json_output.append(
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "content": "-  "},
                    {
                        "type": "link",
                        "url": "https://linkinghub.elsevier.com/retrieve/pii/S1566253524001003",
                        "content": "Adaface",
                    },
                    {
                        "type": "text",
                        "content": " is one of the most widely adopted approaches for training fairer models. Specifically, in the FRCSyn challenge—which focuses on training fair face verification models using synthetic data—most of the top-performing solutions employ the Adaface approach. \n \n <sub>Melzi, P., Tolosana, R., Vera-Rodriguez, R., Kim, M., Rathgeb, C., Liu, X., ... & Marras, M. (2024). FRCSyn-onGoing: Benchmarking and comprehensive evaluation of real and synthetic data to improve face recognition systems. *Information Fusion*, 107, 102322.</sub>\n",
                    },
                ],
            }
        )
        json_output.append(
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "content": "- Data augmentation techniques targeting to a specific task can be applied to improve a model's fairness. For example, ",
                    },
                    {
                        "type": "link",
                        "url": "",
                        "content": "face-swapping augmentation",
                    },
                    {
                        "type": "text",
                        "content": " can be employed in ID document and selfie face verification tasks. \n \n <sub>Moussa, E. M., Sarridis, I., Krasanakis, E., Ramoly, N., Papadopoulos, S., Awal, A. M., & Younes, L. (2025). Face-swapping Based Data Augmentation for ID Document and Selfie Face Verification. In Proceedings of the Winter Conference on Applications of Computer Vision (pp. 1421-1428).</sub>\n",
                    },
                ],
            }
        )
    # print(results_dict["mitigation"])
    # flac_present = any("flac" in text.lower() for text in results_dict["mitigation"])
    # badd_present = any("badd" in text.lower() for text in results_dict["mitigation"])
    # adaface_present = any(
    #     "adaface" in text.lower() for text in results_dict["mitigation"]
    # )

    if len(spurious_correlations) == 1:
        json_output += get_flac_json()
    elif len(spurious_correlations) > 1:
        json_output += get_badd_json()

    if task.lower() == "face verification":
        json_output += get_adaface_json()

    # if flac_present:
    #     json_output += get_flac_json()
    # elif badd_present:
    #     json_output += get_badd_json()
    # elif adaface_present:
    #     json_output += get_adaface_json()

    if return_title:
        return json_output, title  # json.dumps(json_output, indent=4)
    else:
        return json_output


def analysis_md(
    csv_path: str,
    task: str,
    target: str,
    sensitive: List[str],
    sp_th: float = 0.1,
    rep_th: float = 0.1,
):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    representation_bias_result = analyze_representation_bias(df, sensitive)

    # Provide suggestions based on the task and analysis results
    suggestions = []
    results_dict = {"task": task, "biases": [], "mitigation": []}
    bias_threshold = rep_th
    c = 0
    for key, value in representation_bias_result.items():
        if isinstance(value, dict):
            # print(value)
            max_proportion = max(value.values())
            min_proportion = min(value.values())
            if max_proportion - min_proportion > bias_threshold * sum(value.values()):
                suggestions.append(
                    f"There is representation bias for {key} ({(max_proportion-min_proportion)*100:.2f}% gap between most and less represented group)."
                )

                results_dict["biases"].append(suggestions[-1])

    sc = find_spurious_correlations(df, target, sensitive, sp_th)
    if task.lower() == "face verification":
        suggestions.append(
            "Consider using AdaFace for training a fairer face verification model."
        )
        results_dict["mitigation"].append(suggestions[-1])

    elif task.lower() == "image classification":
        if len(sc) == 1:
            suggestions.append(
                f"There is spurious correlation of {(sc[0][2])*100:.2f}% between {sc[0][0]} and {sc[0][1]}."
            )
            results_dict["biases"].append(suggestions[-1])
            results_dict["mitigation"].append(
                "Consider using the FLAC method to mitigate it."
            )
        elif len(sc) > 1:
            for tar, sen, per in sc:
                suggestions.append(
                    f"There is spurious correlation of {per*100:.2f}% between {tar} and {sen}."
                )
                results_dict["biases"].append(suggestions[-1])
            results_dict["mitigation"].append(
                "Given that there are multiple spurious correlations, consider using the BAdd method to mitigate it."
            )

    if len(results_dict["mitigation"]) == 0:
        results_dict["mitigation"].append(
            "Consider using the FLAC method for learning fair represnetations."
        )
    nl = "\n"
    markdown = f"""
# Task: {results_dict['task']}

## Biases:
{''.join([f"- {bias}{nl}" for bias in results_dict['biases']])}

## Mitigation:
{''.join([f"- {mitigation}{nl}" for mitigation in results_dict['mitigation']])}
"""
    flac_present = any("flac" in text.lower() for text in results_dict["mitigation"])
    badd_present = any("badd" in text.lower() for text in results_dict["mitigation"])
    adaface_present = any(
        "adaface" in text.lower() for text in results_dict["mitigation"]
    )

    if flac_present:
        markdown += get_flac_markdown()
    elif badd_present:
        markdown += get_badd_markdown()
    elif adaface_present:
        markdown += get_adaface_markdown()

    return markdown


def analysis(
    csv_path: str,
    task: str,
    target: str,
    sensitive: List[str],
    sp_th: float = 0.1,
    rep_th: float = 0.1,
    output: str = "md",
    return_title: bool = False,
):
    if output == "md":
        return analysis_md(csv_path, task, target, sensitive, sp_th, rep_th)
    elif output == "json":
        return analysis_json(
            csv_path, task, target, sensitive, sp_th, rep_th, return_title
        )
    else:
        raise ValueError("ouput format should be either md or json")


def find_spurious_correlations(
    df, target_column, attribute_columns, threshold=0.01, method="pearson"
):
    """
    Finds spurious correlations between attributes and the target column in a DataFrame.

    Parameters:
        df (DataFrame): The DataFrame containing attributes and the target column.
        attribute_columns (list): List of attribute column names.
        target_column (str): The name of the target column.
        threshold (float): The threshold for correlation coefficient above which correlations are considered significant.
        method (str): The method to compute correlation. Options: 'pearson' (default) or 'spearman'.

    Returns:
        spurious_correlations (list of tuples): List of tuples containing attribute-target pairs with spurious correlations.
    """
    spurious_correlations = []

    if method == "pearson":
        corr_func = pearsonr
    elif method == "spearman":
        corr_func = spearmanr
    else:
        raise ValueError(
            "Invalid correlation method. Please choose 'pearson' or 'spearman'."
        )
    df[target_column], _ = pd.factorize(df[target_column])
    # print(df)
    for column in attribute_columns:
        codes, _ = pd.factorize(df[column])
        correlation, _ = corr_func(codes, df[target_column])
        # print(correlation)
        if abs(correlation) > threshold:
            spurious_correlations.append((column, target_column, abs(correlation)))

    return spurious_correlations


def plot_representation_bias_html(df: pd.DataFrame, sensitive: List[str]) -> str:
    """
    Creates a horizontal barplot showing the distribution of intersectional groups
    defined by the given sensitive attributes, and returns it as an HTML <img> tag.
    """

    # Step 1: Create intersection key
    df["intersection"] = df[sensitive].astype(str).agg(" / ".join, axis=1)
    counts = (
        df["intersection"].value_counts(normalize=True).sort_values(ascending=True)
    )  # ascending for horizontal plot

    # Step 2: Adjust figure height based on number of categories
    n_groups = len(counts)
    height_per_group = 0.2
    min_height = 4
    fig_height = max(min_height, n_groups * height_per_group)

    # Step 3: Create the plot (horizontal)
    plt.figure(figsize=(8, fig_height))
    ax = sns.barplot(x=counts.values, y=counts.index, palette="muted")

    # Add proportion labels to each bar
    for i, (val, label) in enumerate(zip(counts.values, counts.index)):
        ax.text(val + 0.001, i, f"{val:.4f}", va="center")

    max_val = counts.values.max()
    plt.xlim(0, max_val + max_val * 0.1)
    plt.xlabel("Proportion (%)")
    attr_label = " / ".join(sensitive)
    plt.ylabel(f"Intersection of Sensitive Attributes ({attr_label})")
    plt.title("Representation Bias by Sensitive Attribute Intersections")
    plt.tight_layout()

    # Step 4: Convert plot to HTML
    buffer = io.BytesIO()
    plt.savefig("tmp.png", bbox_inches="tight")
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()

    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    html_img = f'<img src="data:image/png;base64,{img_base64}" />'

    return html_img


def analyze_representation_bias(
    df: pd.DataFrame, sensitive: List[str]
) -> Dict[str, Dict[str, float]]:
    """
    Analyzes representation bias with respect to sensitive attributes.

    Parameters:
    csv_path (str): The path to the CSV file.
    sensitive (List[str]): A list of column names of the sensitive attributes.

    Returns:
    Dict[str, Dict[str, float]]: A dictionary with representation bias scores.
    """

    # Initialize the result dictionary
    result = {}

    # Analyze representation bias for each sensitive attribute
    for attribute in sensitive:
        attribute_counts = df[attribute].value_counts(normalize=True)
        result[attribute] = attribute_counts.to_dict()

    return result


def json_to_str_recursively(data, indent=0):
    """Converts a JSON object to a string iteratively and recursively."""
    result_str = ""

    if isinstance(data, list):
        for item in data:
            result_str += json_to_str_recursively(item, indent)
    elif isinstance(data, dict):
        if data.get("type") == "heading":
            result_str += " " * indent + f"{'#' * data['level']} {data['content']}\n"
        elif data.get("type") == "paragraph":
            content = data.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        result_str += " " * indent + item.get("content", "")
                    elif item.get("type") == "inline_code":
                        result_str += f"`{item.get('content', '')}`"
                    elif item.get("type") == "link":
                        result_str += (
                            f"[{item.get('content', '')}]({item.get('url', '')})"
                        )
                    elif item.get("type") == "code":
                        result_str += (
                            "\n"
                            + " " * (indent + 4)
                            + "```"
                            + item.get("language", "")
                            + "\n"
                        )
                        result_str += (
                            " " * (indent + 4) + item.get("content", "") + "\n"
                        )
                        result_str += " " * (indent + 4) + "```"
            else:
                result_str += " " * indent + str(content)
            result_str += "\n"  # newline after paragraph
        elif data.get("type") == "code":
            result_str += " " * indent + "```" + data.get("language", "") + "\n"
            result_str += " " * indent + data.get("content", "") + "\n"
            result_str += " " * indent + "```\n"
        elif data.get("type") == "list":
            result_str += json_to_str_recursively(data.get("content", []), indent)
        else:
            result_str += " " * indent + str(data) + "\n"
    else:
        result_str += " " * indent + str(data) + "\n"

    return result_str


# data = analysis(
#     csv_path="./data/rfw.csv",
#     task="face verification",  # "image classification",
#     target="Gender",
#     sensitive=["Gender", "Race", "Age Category"],
#     sp_th=0.01,
#     rep_th=0.01,
#     output="json",
# )
# print(data)
# print(json_to_str_recursively(data))
